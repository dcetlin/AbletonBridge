"""Shared type definitions for AbletonBridge.

Auto-generated TypedDict definitions for all 255 command parameter schemas.
The MCP server imports these for static analysis — a typo in a param dict
key is caught by mypy/pyright. The Remote Script does not import from here;
it uses the registry's runtime introspection instead.

Regenerate after changing handler signatures:
    python scripts/generate_command_types.py
"""

from .commands import COMMAND_TYPES, MODIFYING_COMMANDS, READONLY_COMMANDS
