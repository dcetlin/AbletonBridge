"""Shared type definitions for AbletonBridge.

This package contains auto-generated TypedDict definitions for all 255
command parameter schemas. Both the MCP server and the Remote Script
can import from here for type-safe command construction.

Regenerate after changing handler signatures:
    python scripts/generate_command_types.py
"""

from .commands import COMMAND_TYPES, MODIFYING_COMMANDS, READONLY_COMMANDS
