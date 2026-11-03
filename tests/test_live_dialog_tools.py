"""The MCP layer of the Live dialog tools, and how a press is sent."""

from __future__ import annotations

import json
import socket
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from MCP_Server.connections.ableton import AbletonCommandError, AbletonConnection, NON_IDEMPOTENT_COMMANDS
from MCP_Server.constants import MODIFYING_COMMANDS
from MCP_Server.tools.session import register_tools


async def _call(name: str, **arguments: Any) -> str:
    server = FastMCP("test")
    register_tools(server)
    result = await server.call_tool(name, arguments)
    content = result[0] if isinstance(result, tuple) else result
    return content[0].text


def _tool(name: str) -> Any:
    server = FastMCP("test")
    register_tools(server)
    return server._tool_manager._tools[name]


@pytest.mark.asyncio
async def test_press_sends_the_index_and_the_message(patch_ableton: MagicMock) -> None:
    patch_ableton.send_command.return_value = {"pressed": 2, "message": "Save?"}
    assert json.loads(await _call("press_live_dialog_button", button_index=2, expected_message="Save?"))["pressed"] == 2
    patch_ableton.send_command.assert_called_once_with(
        "press_live_dialog_button", {"button_index": 2, "expected_message": "Save?"}
    )


@pytest.mark.parametrize("bad", [False, True, 1.0, "1", -1])
@pytest.mark.asyncio
async def test_press_refuses_anything_but_a_whole_index(patch_ableton: MagicMock, bad: Any) -> None:
    with pytest.raises(ToolError):
        await _call("press_live_dialog_button", button_index=bad, expected_message="Save?")
    patch_ableton.send_command.assert_not_called()


@pytest.mark.asyncio
async def test_press_requires_the_message(patch_ableton: MagicMock) -> None:
    with pytest.raises(ToolError):
        await _call("press_live_dialog_button", button_index=0)
    patch_ableton.send_command.assert_not_called()


@pytest.mark.asyncio
async def test_get_dialog_returns_what_live_reports(patch_ableton: MagicMock) -> None:
    patch_ableton.send_command.return_value = {"open_dialog_count": 0}
    assert json.loads(await _call("get_live_dialog")) == {"open_dialog_count": 0}
    patch_ableton.send_command.assert_called_once_with("get_live_dialog")


def test_annotations_say_what_each_tool_does() -> None:
    read = _tool("get_live_dialog").annotations
    press = _tool("press_live_dialog_button").annotations
    assert read.readOnlyHint is True
    assert press.destructiveHint is True and press.idempotentHint is False and press.readOnlyHint is False


@pytest.mark.parametrize("name", ["press_live_dialog_button", "delete_time", "delete_arrangement_clip"])
def test_commands_annotated_non_idempotent_are_never_retried(name: str) -> None:
    assert name in NON_IDEMPOTENT_COMMANDS


def _connection() -> AbletonConnection:
    connection = AbletonConnection(host="localhost", port=9877)
    connection.sock = MagicMock()
    return connection


def test_a_dropped_connection_presses_only_once() -> None:
    connection = _connection()
    with (
        patch.object(connection, "receive_full_response", side_effect=socket.timeout("timed out")) as receive,
        patch.object(connection, "connect", return_value=True) as reconnect,
    ):
        with pytest.raises(AbletonCommandError, match="failed after 1"):
            connection.send_command("press_live_dialog_button", {"button_index": 0, "expected_message": "Save?"})
    assert receive.call_count == 1
    reconnect.assert_not_called()


@pytest.mark.parametrize(
    "error",
    [
        pytest.param({"code": "timeout", "may_have_landed": False}, id="timeout"),
        pytest.param({"code": "unavailable"}, id="scheduling-unavailable"),
    ],
)
def test_a_temporary_error_is_retried_once(error: dict[str, Any]) -> None:
    connection = _connection()
    temporary = {"status": "error", "message": "busy", **error}
    answers = [temporary, {"status": "success", "result": {"ok": True}}]

    def reconnect() -> bool:
        connection.sock = MagicMock()
        return True

    with (
        patch.object(connection, "receive_full_response", side_effect=answers),
        patch.object(connection, "connect", side_effect=reconnect),
    ):
        assert connection.send_command("get_session_info") == {"ok": True}


def test_a_timeout_that_may_have_landed_is_not_retried() -> None:
    connection = _connection()
    landed = {"status": "error", "code": "timeout", "message": "slow", "may_have_landed": True}
    with patch.object(connection, "receive_full_response", return_value=landed) as receive:
        with pytest.raises(AbletonCommandError) as error:
            connection.send_command("set_tempo", {"tempo": 120})
    assert receive.call_count == 1
    assert error.value.may_have_landed is True


def test_a_dropped_modifying_command_says_it_may_have_landed() -> None:
    connection = _connection()
    with patch.object(connection, "receive_full_response", side_effect=socket.timeout("timed out")):
        with pytest.raises(AbletonCommandError) as error:
            connection.send_command("press_live_dialog_button", {"button_index": 0, "expected_message": "Save?"})
    assert error.value.may_have_landed is True


def test_the_press_gets_the_longer_modifying_timeout() -> None:
    assert "press_live_dialog_button" in MODIFYING_COMMANDS


def test_a_refusal_is_not_retried_and_keeps_its_detail() -> None:
    connection = _connection()
    refusal = {"status": "error", "code": "invalid_input", "message": "no", "may_have_landed": False}
    with patch.object(connection, "receive_full_response", return_value=refusal) as receive:
        with pytest.raises(AbletonCommandError) as error:
            connection.send_command("get_live_dialog")
    assert receive.call_count == 1
    assert error.value.code == "invalid_input"
