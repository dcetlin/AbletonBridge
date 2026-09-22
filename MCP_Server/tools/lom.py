"""Generic LOM access tools."""
import json
from typing import Union
from mcp.server.fastmcp import Context
from MCP_Server.tools._base import _tool_handler
from MCP_Server.connections.ableton import get_ableton_connection


def register_tools(mcp):
    @mcp.tool()
    @_tool_handler("getting LOM value")
    def lom_get(ctx: Context, path: str) -> str:
        """Read any Live Object Model property by path.
        Use lom_describe first to explore available properties.
        Path: "tempo", "tracks[0].name", "tracks[0].devices[1].parameters[3].value"
        """
        ableton = get_ableton_connection()
        return json.dumps(ableton.send_command("lom_get", {"path": path}))

    @mcp.tool()
    @_tool_handler("setting LOM value")
    def lom_set(ctx: Context, path: str, value: Union[float, int, str, bool]) -> str:
        """Set any Live Object Model property by path.

        No validation is performed — the value is passed straight to the LOM,
        which enforces its own types/bounds. Prefer a named command (e.g.
        set_tempo, set_device_parameter) when one exists; this is the generic
        escape hatch for the long tail. Pass numbers as numbers (tempo=140.0),
        booleans as booleans (mute=true), names as strings.
        """
        ableton = get_ableton_connection()
        return json.dumps(ableton.send_command("lom_set", {"path": path, "value": value}))

    @mcp.tool()
    @_tool_handler("describing LOM object")
    def lom_describe(ctx: Context, path: str = "", depth: int = 1) -> str:
        """Introspect any LOM object. Empty path = Song. depth 0-3."""
        ableton = get_ableton_connection()
        return json.dumps(ableton.send_command("lom_describe", {"path": path, "depth": depth}), indent=2)
