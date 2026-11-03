"""A slow M4L ping must not hold up the dashboard."""

from __future__ import annotations

import socket
import threading
import time
import urllib.request
from unittest.mock import MagicMock, patch

import pytest

import MCP_Server.state as state
from MCP_Server.dashboard import server as dashboard


def _fetch(port: int, path: str) -> float:
    started = time.time()
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as response:
        assert response.status == 200
    return time.time() - started


@pytest.fixture
def slow_bridge(monkeypatch: pytest.MonkeyPatch) -> tuple[MagicMock, threading.Event]:
    release = threading.Event()
    bridge = MagicMock(_connected=True)
    bridge.ping.side_effect = lambda: release.wait(5) and True
    monkeypatch.setattr(state, "m4l_connection", bridge)
    monkeypatch.setitem(state.m4l_ping_cache, "timestamp", 0.0)
    monkeypatch.setitem(state.m4l_ping_cache, "result", False)
    yield bridge, release
    release.set()


def test_status_without_wait_returns_at_once_and_refreshes(slow_bridge: tuple[MagicMock, threading.Event]) -> None:
    bridge, release = slow_bridge
    assert dashboard.get_m4l_status(wait=False) == (True, False)
    while not bridge.ping.called:
        time.sleep(0.01)
    assert dashboard.get_m4l_status(wait=False) == (True, False)
    assert bridge.ping.call_count == 1
    release.set()
    while state.m4l_ping_cache["result"] is not True:
        time.sleep(0.01)
    assert dashboard.get_m4l_status(wait=False) == (True, True)
    assert bridge.ping.call_count == 1


def test_status_with_wait_returns_the_ping_result(slow_bridge: tuple[MagicMock, threading.Event]) -> None:
    _, release = slow_bridge
    release.set()
    assert dashboard.get_m4l_status() == (True, True)


def test_dashboard_answers_during_a_slow_ping(
    monkeypatch: pytest.MonkeyPatch, slow_bridge: tuple[MagicMock, threading.Event]
) -> None:
    bridge, _ = slow_bridge
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = int(s.getsockname()[1])
    monkeypatch.setattr(state, "DASHBOARD_PORT", port)
    with patch.object(dashboard.webbrowser, "open"):
        dashboard.start_dashboard_server()
        try:
            deadline = time.time() + 5
            while True:
                try:
                    _fetch(port, "/")
                    break
                except OSError:
                    assert time.time() < deadline
                    time.sleep(0.05)
            assert _fetch(port, "/api/status") < 1.0  # starts the slow ping
            while not bridge.ping.called:
                time.sleep(0.01)
            assert _fetch(port, "/") < 1.0
            assert _fetch(port, "/api/status") < 1.0
        finally:
            dashboard.stop_dashboard_server()
