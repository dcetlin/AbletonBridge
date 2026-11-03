"""The dashboard keeps trying when its port is busy at startup."""

from __future__ import annotations

import socket
import time
import urllib.request
from unittest.mock import patch

import pytest

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
    monkeypatch.setenv("ABLETON_BRIDGE_OPEN_DASHBOARD", "1")
    holder = socket.socket()
    holder.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    holder.bind(("127.0.0.1", port))
    holder.listen()
    accepted: list[bool] = []

    def open_browser(_url: str) -> None:
        with socket.socket() as client:
            accepted.append(client.connect_ex(("127.0.0.1", port)) == 0)

    with patch.object(dashboard.webbrowser, "open", side_effect=open_browser) as browser:
        dashboard.start_dashboard_server()
        try:
            time.sleep(0.3)
            browser.assert_not_called()
            holder.close()
            assert _wait_for(lambda: _responds(port))
            browser.assert_called_once()
            assert accepted == [True]  # the port accepts by the time the browser opens
        finally:
            dashboard.stop_dashboard_server()


def test_stopping_during_the_retry_wait_ends_the_loop(monkeypatch) -> None:
    port = _free_port()
    monkeypatch.setattr(state, "DASHBOARD_PORT", port)
    monkeypatch.setattr(dashboard, "DASHBOARD_RETRY_SECONDS", 0.1)
    monkeypatch.setenv("ABLETON_BRIDGE_OPEN_DASHBOARD", "1")
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


@pytest.mark.parametrize("value", [None, "0", ""])
def test_browser_stays_closed_unless_asked_for(monkeypatch, value) -> None:
    port = _free_port()
    monkeypatch.setattr(state, "DASHBOARD_PORT", port)
    if value is None:
        monkeypatch.delenv("ABLETON_BRIDGE_OPEN_DASHBOARD", raising=False)
    else:
        monkeypatch.setenv("ABLETON_BRIDGE_OPEN_DASHBOARD", value)
    with patch.object(dashboard.webbrowser, "open") as browser:
        dashboard.start_dashboard_server()
        try:
            assert _wait_for(lambda: _responds(port))
            browser.assert_not_called()
        finally:
            dashboard.stop_dashboard_server()
