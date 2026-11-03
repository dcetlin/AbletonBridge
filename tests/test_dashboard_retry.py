"""The dashboard keeps trying when its port is busy at startup."""

from __future__ import annotations

import socket
import time
import urllib.request
from unittest.mock import patch

import MCP_Server.state as state
from MCP_Server.dashboard import server as dashboard


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _responds(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status", timeout=1) as r:
            return r.status == 200
    except OSError:
        return False


def _wait_for(check, seconds: float = 10.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if check():
            return True
        time.sleep(0.05)
    return False


def test_dashboard_comes_up_once_its_port_is_free(monkeypatch) -> None:
    port = _free_port()
    monkeypatch.setattr(state, "DASHBOARD_PORT", port)
    monkeypatch.setattr(dashboard, "DASHBOARD_RETRY_SECONDS", 0.1)
    holder = socket.socket()
    holder.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    holder.bind(("127.0.0.1", port))
    holder.listen()
    with patch.object(dashboard.webbrowser, "open") as browser:
        dashboard.start_dashboard_server()
        try:
            time.sleep(0.3)
            browser.assert_not_called()
            holder.close()
            assert _wait_for(lambda: _responds(port))
            browser.assert_called_once()
        finally:
            dashboard.stop_dashboard_server()


def test_stopping_during_the_retry_wait_ends_the_loop(monkeypatch) -> None:
    port = _free_port()
    monkeypatch.setattr(state, "DASHBOARD_PORT", port)
    monkeypatch.setattr(dashboard, "DASHBOARD_RETRY_SECONDS", 0.1)
    holder = socket.socket()
    holder.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    holder.bind(("127.0.0.1", port))
    holder.listen()
    with patch.object(dashboard.webbrowser, "open") as browser:
        dashboard.start_dashboard_server()
        time.sleep(0.2)
        dashboard.stop_dashboard_server()
        holder.close()
        time.sleep(0.5)
        browser.assert_not_called()
        assert not _responds(port)

