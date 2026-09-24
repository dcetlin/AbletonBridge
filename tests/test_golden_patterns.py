"""Tests enforcing golden patterns — catch drift before it ships."""

import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent
HANDLERS_DIR = ROOT / "AbletonBridge_Remote_Script" / "handlers"
TOOLS_DIR = ROOT / "MCP_Server" / "tools"


# ---------------------------------------------------------------------------
# 1. Handler import completeness
# ---------------------------------------------------------------------------

def test_all_handler_modules_imported():
    """Every handler .py is imported in handlers/__init__.py."""
    handler_files = {
        f.stem
        for f in HANDLERS_DIR.glob("*.py")
        if not f.name.startswith("_") and f.name != "__init__.py"
    }
    init_path = HANDLERS_DIR / "__init__.py"
    init_text = init_path.read_text()

    init_imports = set()
    for line in init_text.splitlines():
        m = re.match(r"from \. import (\w+)", line)
        if m:
            init_imports.add(m.group(1))

    missing = handler_files - init_imports
    assert not missing, f"Handler modules not imported in __init__.py: {missing}"


def test_all_handler_modules_in_all():
    """Every handler .py is listed in handlers/__init__.__all__."""
    handler_files = {
        f.stem
        for f in HANDLERS_DIR.glob("*.py")
        if not f.name.startswith("_") and f.name != "__init__.py"
    }
    init_path = HANDLERS_DIR / "__init__.py"
    init_text = init_path.read_text()

    all_match = re.search(r"__all__\s*=\s*\[(.*?)\]", init_text, re.DOTALL)
    assert all_match, "handlers/__init__.py has no __all__"
    all_items = set(re.findall(r'"(\w+)"', all_match.group(1)))

    missing = handler_files - all_items
    assert not missing, f"Handler modules not in __all__: {missing}"


# ---------------------------------------------------------------------------
# 2. Command → MCP tool coverage
# ---------------------------------------------------------------------------

def test_every_command_reachable_via_mcp():
    """Every registered command is called by at least one MCP tool module."""
    sys.path.insert(0, str(ROOT / "AbletonBridge_Remote_Script"))
    from handlers._registry import get_registry
    sys.path.pop(0)

    registered = set(get_registry().keys())

    called = set()
    for tool_file in TOOLS_DIR.glob("*.py"):
        if tool_file.name.startswith("_"):
            continue
        text = tool_file.read_text()
        for m in re.finditer(r'send_command\(\s*["\'](\w+)["\']', text):
            called.add(m.group(1))
        for m in re.finditer(r'send_command_with_retry\(\s*["\'](\w+)["\']', text):
            called.add(m.group(1))

    orphaned = registered - called

    # Known orphans: commands in the registry but intentionally not exposed as
    # individual MCP tools (used internally or via different MCP tool paths)
    KNOWN_ORPHANS = {
        "_reload_handlers",      # internal TCP command
        "search_browser",        # MCP tool does local cache search, not send_command
        "get_browser_item",      # used internally by browser tools
        "set_loop_start",        # covered by set_loop_region MCP tool
        "set_loop_length",       # covered by set_loop_region MCP tool
        "set_loop_end",          # covered by set_loop_region MCP tool
    }
    unexpected = orphaned - KNOWN_ORPHANS
    assert not unexpected, f"Commands registered but no MCP tool calls them: {unexpected}"


# ---------------------------------------------------------------------------
# 3. Annotation consistency
# ---------------------------------------------------------------------------

def test_destructive_commands_have_mcp_annotations():
    """Every destructive command's MCP tool uses annotations=."""
    sys.path.insert(0, str(ROOT))
    from shared.commands import COMMAND_ANNOTATIONS
    sys.path.pop(0)

    destructive = {
        name for name, ann in COMMAND_ANNOTATIONS.items()
        if ann.get("destructive", False)
    }

    # Find which destructive commands have annotations= in their tool module
    unannotated = set()
    for cmd_name in destructive:
        found = False
        for tool_file in TOOLS_DIR.glob("*.py"):
            if tool_file.name.startswith("_"):
                continue
            text = tool_file.read_text()
            if f'send_command("{cmd_name}"' in text or f"send_command('{cmd_name}'" in text:
                # Check nearby @mcp.tool has annotations=
                lines = text.splitlines()
                for i, line in enumerate(lines):
                    if f'send_command("{cmd_name}"' in line or f"send_command('{cmd_name}'" in line:
                        # Look backwards for @mcp.tool
                        context = "\n".join(lines[max(0, i - 30):i])
                        if "annotations=" in context:
                            found = True
                            break
                if found:
                    break
        if not found:
            unannotated.add(cmd_name)

    assert not unannotated, (
        f"Destructive commands without annotations= on their MCP tool: {unannotated}"
    )


# ---------------------------------------------------------------------------
# 4. README count drift
# ---------------------------------------------------------------------------

def test_readme_tool_count():
    """README headline tool count matches actual."""
    readme = (ROOT / "README.md").read_text()
    m = re.search(r"(\d+) MCP tools", readme)
    assert m, "README doesn't mention MCP tool count"
    readme_count = int(m.group(1))

    actual = 0
    for tool_file in TOOLS_DIR.glob("*.py"):
        actual += tool_file.read_text().count("@mcp.tool")

    assert readme_count == actual, (
        f"README says {readme_count} tools but actual is {actual}"
    )


def test_readme_command_count():
    """README headline command count matches actual."""
    readme = (ROOT / "README.md").read_text()
    m = re.search(r"(\d+) handler commands", readme)
    assert m, "README doesn't mention handler command count"
    readme_count = int(m.group(1))

    sys.path.insert(0, str(ROOT / "AbletonBridge_Remote_Script"))
    from handlers._registry import get_registry
    sys.path.pop(0)

    actual = len(get_registry())
    assert readme_count == actual, (
        f"README says {readme_count} commands but actual is {actual}"
    )
