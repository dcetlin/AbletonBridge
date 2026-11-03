"""The server's services start once and outlive any one client."""

from __future__ import annotations

import asyncio
import os
import signal
import socket
import subprocess
import sys
import threading
import time
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
    m4l.retire.assert_called_once()
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


def test_sigterm_exits_normally_under_sse(monkeypatch: pytest.MonkeyPatch) -> None:
    handlers: dict[int, Any] = {}
    monkeypatch.setenv("ABLETON_BRIDGE_TRANSPORT", "sse")
    monkeypatch.setattr(server.signal, "signal", handlers.__setitem__)
    monkeypatch.setattr(server, "_acquire_singleton_lock", MagicMock())
    monkeypatch.setattr(state, "singleton_lock_sock", None)
    monkeypatch.setattr(server.mcp, "run", MagicMock())
    server.main()
    assert set(handlers) == {signal.SIGTERM}
    with pytest.raises(SystemExit) as exit_info:
        handlers[signal.SIGTERM](signal.SIGTERM, None)
    assert exit_info.value.code == 0


@pytest.mark.parametrize("signum", [signal.SIGINT, signal.SIGTERM])
def test_stdio_server_exits_at_once_on_signal_with_stdin_open(signum: signal.Signals) -> None:
    # Services are stubbed out, so no ports are touched.
    env = {**os.environ, "ABLETON_BRIDGE_TRANSPORT": "stdio", "PYTHONUNBUFFERED": "1"}
    code = (
        "from MCP_Server import server\n"
        "server._start_services = lambda: None\n"
        "print('up', flush=True)\n"
        "server.main()\n"
    )
    process = subprocess.Popen(
        [sys.executable, "-c", code],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    try:
        assert process.stdout is not None
        assert process.stdout.readline().strip() == b"up"
        time.sleep(1.0)  # let main() install its handlers and start reading stdin
        process.send_signal(signum)
        assert process.wait(timeout=10) == 128 + signum
    finally:
        process.kill()
        process.wait()


def test_stop_and_exit_stops_services_then_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[object] = []
    monkeypatch.setattr(server, "_stop_services", lambda: calls.append("stop"))
    monkeypatch.setattr(server.os, "_exit", calls.append)
    server._stop_and_exit(signal.SIGINT, None)
    assert calls == ["stop", 130]


def test_stop_and_exit_exits_even_if_stopping_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    exits: list[int] = []

    def fail() -> None:
        raise OSError("stop failed")

    monkeypatch.setattr(server, "_stop_services", fail)
    monkeypatch.setattr(server.os, "_exit", exits.append)
    with pytest.raises(OSError):
        server._stop_and_exit(signal.SIGTERM, None)
    assert exits == [143]


def test_stop_and_exit_exits_even_if_stopping_hangs(monkeypatch: pytest.MonkeyPatch) -> None:
    exited = threading.Event()
    monkeypatch.setattr(server, "STOP_TIMEOUT_SECONDS", 0.05)
    monkeypatch.setattr(server, "_stop_services", lambda: exited.wait(5))
    monkeypatch.setattr(server.os, "_exit", lambda _code: exited.set())
    server._stop_and_exit(signal.SIGTERM, None)
    assert exited.is_set()


def test_start_services_records_the_event_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("get_ableton_connection", "start_dashboard_server", "_m4l_auto_connect", "_browser_cache_warmup"):
        monkeypatch.setattr(server, name, MagicMock())
    monkeypatch.setattr(state, "singleton_lock_sock", MagicMock())
    monkeypatch.setattr(state, "main_loop", None)

    async def run() -> bool:
        server._start_services()
        return state.main_loop is asyncio.get_running_loop()

    assert asyncio.run(run())


def test_auto_connect_reconnects_drains_and_sets_a_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    conn = MagicMock(_connected=False)
    conn._send_lock = threading.Lock()
    conn.recv_sock.recvfrom.return_value = (b"x", None)
    conn._parse_m4l_response.return_value = {"status": "success"}
    monkeypatch.setattr(server, "M4LConnection", MagicMock(return_value=conn))
    monkeypatch.setattr(state, "m4l_connection", None)
    server._m4l_auto_connect()
    assert conn.connect.call_count == 2  # once on creation, once to reopen
    conn._drain_recv_socket.assert_called_once()
    conn.recv_sock.settimeout.assert_called_once_with(2.0)


def test_auto_connect_holds_the_send_lock_during_the_exchange(monkeypatch: pytest.MonkeyPatch) -> None:
    held: list[bool] = []
    conn = MagicMock()
    conn.connect.return_value = True
    conn._connected = True
    conn._send_lock = threading.Lock()
    conn.recv_sock.recvfrom.side_effect = lambda _n: (held.append(conn._send_lock.locked()), (b"x", None))[1]
    conn._parse_m4l_response.return_value = {"status": "success"}
    monkeypatch.setattr(server, "M4LConnection", MagicMock(return_value=conn))
    monkeypatch.setattr(state, "m4l_connection", None)
    server._m4l_auto_connect()
    assert held == [True]
    assert state.m4l_ping_cache["result"] is True


def test_auto_connect_stops_when_replaced(monkeypatch: pytest.MonkeyPatch) -> None:
    conn = MagicMock(_connected=True)
    conn._send_lock = threading.Lock()

    def replaced_during_first_attempt(_n: int) -> None:
        monkeypatch.setattr(state, "m4l_connection", MagicMock())
        raise socket.timeout

    conn.recv_sock.recvfrom.side_effect = replaced_during_first_attempt
    monkeypatch.setattr(server, "M4LConnection", MagicMock(return_value=conn))
    monkeypatch.setattr(server.time, "sleep", lambda _s: None)
    monkeypatch.setattr(state, "m4l_connection", None)
    server._m4l_auto_connect()
    assert conn.send_sock.sendto.call_count == 1


def test_browser_cache_warmup_waits_for_live_without_a_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    event = MagicMock()
    monkeypatch.setattr(state, "ableton_connected_event", event)
    monkeypatch.setattr(server, "load_browser_cache_from_disk", lambda: False)
    monkeypatch.setattr(server, "populate_browser_cache", populate := MagicMock())
    monkeypatch.setattr(server.time, "sleep", lambda _: None)
    server._browser_cache_warmup()
    event.wait.assert_called_once_with()
    populate.assert_called_once()



def test_report_progress_reaches_the_client_from_a_worker_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    from MCP_Server.tools._base import _report_progress

    seen: list[tuple[float, float, str | None]] = []

    class Ctx:
        async def report_progress(self, current: float, total: float, message: str | None = None) -> None:
            seen.append((current, total, message))

    async def run() -> None:
        monkeypatch.setattr(state, "main_loop", asyncio.get_running_loop())
        await asyncio.to_thread(_report_progress, Ctx(), 1, 4, "step")
        await asyncio.sleep(0.05)

    asyncio.run(run())
    assert seen == [(1, 4, "step")]


def test_report_progress_without_a_loop_is_silent(monkeypatch: pytest.MonkeyPatch) -> None:
    from MCP_Server.tools._base import _report_progress

    monkeypatch.setattr(state, "main_loop", None)
    ctx = MagicMock()
    _report_progress(ctx, 1, 4, "step")
    ctx.report_progress.assert_not_called()


def test_report_progress_skips_a_stopped_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    from MCP_Server.tools._base import _report_progress

    loop = asyncio.new_event_loop()
    try:
        monkeypatch.setattr(state, "main_loop", loop)
        ctx = MagicMock()
        _report_progress(ctx, 1, 4, "step")
        ctx.report_progress.assert_not_called()
    finally:
        loop.close()

