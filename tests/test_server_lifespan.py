"""The server's services start once and outlive any one client."""

from __future__ import annotations

import asyncio
import signal
from typing import Any
from unittest.mock import MagicMock

import pytest

import MCP_Server.state as state
from MCP_Server import server


seen_registered: list[object] = []


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    seen: list[str] = []
    monkeypatch.setattr(server, "_services_started", False)
    monkeypatch.setattr(server, "_start_services", lambda: seen.append("start"))
    def stop() -> None:
        seen.append("stop")

    monkeypatch.setattr(server, "_stop_services", stop)
    seen_registered.clear()
    monkeypatch.setattr(server.atexit, "register", lambda f: (seen_registered.append(f), seen.append("atexit")))
    return seen


def _connect_and_leave() -> None:
    async def run() -> None:
        fake: Any = None
        async with server.server_lifespan(fake):
            await asyncio.sleep(0)

    asyncio.run(run())


def test_services_survive_the_last_client_leaving(calls: list[str]) -> None:
    _connect_and_leave()
    assert "start" in calls and "stop" not in calls


def test_services_start_once_across_clients(calls: list[str]) -> None:
    for _ in range(3):
        _connect_and_leave()
    assert calls.count("start") == 1
    assert calls.count("atexit") == 1
    assert seen_registered == [server._stop_services]


def test_concurrent_clients_share_one_start(calls: list[str]) -> None:
    async def client() -> None:
        fake: Any = None
        async with server.server_lifespan(fake):
            await asyncio.sleep(0)

    async def run() -> None:
        await asyncio.gather(client(), client(), client())

    asyncio.run(run())
    assert calls.count("start") == 1


def test_stop_services_disconnects_and_releases_the_lock(monkeypatch: pytest.MonkeyPatch) -> None:
    ableton, m4l, lock = MagicMock(), MagicMock(), MagicMock()
    monkeypatch.setattr(server, "stop_dashboard_server", dashboard := MagicMock())
    monkeypatch.setattr(server, "_release_singleton_lock", release := MagicMock())
    monkeypatch.setattr(state, "ableton_connection", ableton)
    monkeypatch.setattr(state, "m4l_connection", m4l)
    monkeypatch.setattr(state, "singleton_lock_sock", lock)
    server._stop_services()
    dashboard.assert_called_once()
    ableton.disconnect.assert_called_once()
    m4l.disconnect.assert_called_once()
    release.assert_called_once_with(lock)
    assert state.ableton_connection is None and state.m4l_connection is None and state.singleton_lock_sock is None


def test_second_instance_exits_on_lock_conflict(monkeypatch: pytest.MonkeyPatch) -> None:
    def conflict() -> None:
        raise RuntimeError("already running")

    monkeypatch.setattr(state, "singleton_lock_sock", None)
    monkeypatch.setattr(server, "_acquire_singleton_lock", conflict)
    with pytest.raises(SystemExit) as exit_info:
        server._start_services()
    assert exit_info.value.code == 1


@pytest.mark.parametrize(("transport", "installs"), [("sse", True), ("stdio", False)])
def test_sigterm_exits_normally_only_under_sse(
    monkeypatch: pytest.MonkeyPatch, transport: str, installs: bool
) -> None:
    handlers: dict[int, Any] = {}
    monkeypatch.setenv("ABLETON_BRIDGE_TRANSPORT", transport)
    monkeypatch.setattr(server.signal, "signal", handlers.__setitem__)
    monkeypatch.setattr(server, "_acquire_singleton_lock", MagicMock())
    monkeypatch.setattr(state, "singleton_lock_sock", None)
    monkeypatch.setattr(server.mcp, "run", MagicMock())
    server.main()
    assert (signal.SIGTERM in handlers) is installs
    if installs:
        with pytest.raises(SystemExit) as exit_info:
            handlers[signal.SIGTERM](signal.SIGTERM, None)
        assert exit_info.value.code == 0


def test_browser_cache_warmup_waits_for_live_without_a_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    event = MagicMock()
    monkeypatch.setattr(state, "ableton_connected_event", event)
    monkeypatch.setattr(server, "load_browser_cache_from_disk", lambda: False)
    monkeypatch.setattr(server, "populate_browser_cache", populate := MagicMock())
    monkeypatch.setattr(server.time, "sleep", lambda _: None)
    server._browser_cache_warmup()
    event.wait.assert_called_once_with()
    populate.assert_called_once()

