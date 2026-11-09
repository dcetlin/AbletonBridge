"""insert_device_by_name must not report success when Live inserted nothing."""
import json
from unittest.mock import MagicMock, patch

import pytest


def _tool(mcp_name, conn):
    from mcp.server.fastmcp import FastMCP
    from MCP_Server.tools.devices import register_tools
    mcp = FastMCP("test")
    register_tools(mcp)
    return mcp._tool_manager._tools[mcp_name].fn


@pytest.mark.asyncio
@pytest.mark.parametrize("reply, ok", [
    ({"inserted": True, "device_name": "EQ Eight", "track_index": 3}, True),
    ({"inserted": False, "reason": "insert_device requires Live 12.3+"}, False),
])
async def test_insert_device_reports_what_landed(reply, ok):
    conn = MagicMock()
    conn.send_command.return_value = reply
    with patch("MCP_Server.tools.devices.get_ableton_connection", return_value=conn):
        result = json.loads(await _tool("insert_device_by_name", conn)(MagicMock(), track_index=3, device_name="EQ Eight"))
    assert (result["status"] == "ok") is ok
    if not ok:
        assert "12.3" in result["message"]
