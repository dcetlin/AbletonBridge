"""A slow M4L ping must not hold up the dashboard."""

from __future__ import annotations

import socket
import threading
import time
import urllib.request
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

import MCP_Server.state as state
from MCP_Server.dashboard import server as dashboard


def _wait_for(check: Callable[[], bool], seconds: float = 5.0) -> None:
    deadline = time.time() + seconds
    while not check():
        assert time.time() < deadline, "timed out"
        time.sleep(0.005)


def _fetch(port: int, path: str) -> float:
    started = time.time()
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as response:
        assert response.status == 200
    return time.time() - started


@dataclass
class Bridge:
    mock: MagicMock
    release: threading.Event


@pytest.fixture
def bridge(monkeypatch: pytest.MonkeyPatch) -> Iterator[Bridge]:
    """A connected bridge whose ping blocks until released, then answers True."""
    release = threading.Event()
    mock = MagicMock(_connected=True)
    mock.ping.side_effect = lambda: bool(release.wait(5))
    monkeypatch.setattr(state, "m4l_connection", mock)
    monkeypatch.setitem(state.m4l_ping_cache, "timestamp", 0.0)
    monkeypatch.setitem(state.m4l_ping_cache, "result", False)
    yield Bridge(mock, release)
    release.set()
    _wait_for(lambda: not state.m4l_ping_lock.locked())


def test_no_wait_returns_at_once_and_refreshes(bridge: Bridge) -> None:
    assert dashboard.get_m4l_status(wait=False) == (True, False)
    _wait_for(lambda: bridge.mock.ping.called)
    assert dashboard.get_m4l_status(wait=False) == (True, False)
    assert bridge.mock.ping.call_count == 1
    bridge.release.set()
    _wait_for(lambda: state.m4l_ping_cache["result"] is True)
    assert dashboard.get_m4l_status(wait=False) == (True, True)
    assert bridge.mock.ping.call_count == 1


def test_wait_returns_the_ping_result(bridge: Bridge) -> None:
    bridge.release.set()
    assert dashboard.get_m4l_status() == (True, True)


def test_wait_waits_for_a_running_ping_instead_of_reporting_the_old_result(bridge: Bridge) -> None:
    dashboard.get_m4l_status(wait=False)
    _wait_for(lambda: bridge.mock.ping.called)
    results: list[tuple[bool, bool]] = []
    waiter = threading.Thread(target=lambda: results.append(dashboard.get_m4l_status()))
    waiter.start()
    time.sleep(0.05)
    assert not results
    bridge.release.set()
    waiter.join(5)
    assert results == [(True, True)]
    assert bridge.mock.ping.call_count == 1


def test_failed_thread_start_does_not_stick_the_lock(bridge: Bridge) -> None:
    with patch.object(dashboard.threading.Thread, "start", side_effect=RuntimeError("no threads")):
        assert dashboard.get_m4l_status(wait=False) == (True, False)
    assert not state.m4l_ping_lock.locked()
    bridge.release.set()
    dashboard.get_m4l_status(wait=False)
    _wait_for(lambda: state.m4l_ping_cache["result"] is True)


def test_ping_failure_is_cached_as_not_responding(bridge: Bridge) -> None:
    bridge.mock.ping.side_effect = OSError("gone")
    state.m4l_ping_cache["result"] = True
    assert dashboard.get_m4l_status() == (True, False)
    assert not state.m4l_ping_lock.locked()


def test_cache_age_counts_from_when_the_ping_finished(bridge: Bridge, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(state, "M4L_PING_CACHE_TTL", 0.1)
    bridge.mock.ping.side_effect = lambda: time.sleep(0.2) or True
    dashboard.get_m4l_status()
    assert dashboard.get_m4l_status() == (True, True)
    assert bridge.mock.ping.call_count == 1


def test_sockets_not_ready_skips_the_ping(bridge: Bridge) -> None:
    bridge.mock._connected = False
    assert dashboard.get_m4l_status() == (False, False)
    bridge.mock.ping.assert_not_called()


def test_reload_reports_what_the_script_returned(monkeypatch: pytest.MonkeyPatch) -> None:
    connection = MagicMock()
    connection.send_command.return_value = {"reloaded": "started", "message": "Reload dispatched"}
    monkeypatch.setattr("MCP_Server.connections.ableton.get_ableton_connection", lambda: connection)
    deploy = MagicMock(returncode=0, stdout="deployed", stderr="")
    with patch("subprocess.run", return_value=deploy):
        result = dashboard._do_reload_remote_script()
    assert result["status"] == "ok"
    assert result["message"] == "Deployed. Reload dispatched"


def test_dashboard_answers_during_a_slow_ping(monkeypatch: pytest.MonkeyPatch, bridge: Bridge) -> None:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = int(s.getsockname()[1])
    monkeypatch.setattr(state, "DASHBOARD_PORT", port)

    def page_is_up() -> bool:
        try:
            _fetch(port, "/")
            return True
        except OSError:
            return False

    with patch.object(dashboard.webbrowser, "open"):
        dashboard.start_dashboard_server()
        try:
            _wait_for(page_is_up)
            assert _fetch(port, "/api/status") < 1.0  # starts the slow ping
            _wait_for(lambda: bridge.mock.ping.called)
            assert _fetch(port, "/") < 1.0
            assert _fetch(port, "/api/status") < 1.0
        finally:
            dashboard.stop_dashboard_server()
