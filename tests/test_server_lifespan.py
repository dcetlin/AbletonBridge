"""The server's services start once and outlive any one client."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from MCP_Server import server


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    seen: list[str] = []
    monkeypatch.setattr(server, "_services_started", False)
    monkeypatch.setattr(server, "_start_services", lambda: seen.append("start"))
    monkeypatch.setattr(server.atexit, "register", lambda f: seen.append(f"atexit:{f.__name__}"))
    monkeypatch.setattr(server, "_stop_services", lambda: seen.append("stop"))
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
    assert sum(c.startswith("atexit") for c in calls) == 1


def test_overlapping_clients_share_one_start(calls: list[str]) -> None:
    async def run() -> None:
        fake: Any = None
        async with server.server_lifespan(fake):
            async with server.server_lifespan(fake):
                await asyncio.sleep(0)

    asyncio.run(run())
    assert calls.count("start") == 1
