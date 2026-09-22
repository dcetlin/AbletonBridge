#!/usr/bin/env python3
"""Generate TypedDict definitions from the command registry.

Run after changing handler function signatures:
    python scripts/generate_command_types.py

Outputs shared/commands.py with a TypedDict for each registered command's
params, plus lookup dicts for command metadata.
"""

import hashlib
import inspect
import sys
import os
import textwrap
from pathlib import Path

# Import the registry directly (avoid __init__.py which needs _Framework)
sys.path.insert(0, str(Path(__file__).parent.parent / "AbletonBridge_Remote_Script"))

from handlers._registry import get_registry, _SENTINEL
from handlers import (
    session, tracks, clips, mixer, devices,
    browser, scenes, arrangement, audio, midi, automation,
    lom,
)


def _python_type_to_str(annotation) -> str:
    """Convert a Python type annotation to a string for code generation."""
    if annotation is inspect.Parameter.empty or annotation is None:
        return "Any"

    # Handle union types (int | None)
    origin = getattr(annotation, "__origin__", None)
    if origin is type(int | str):  # types.UnionType
        args = annotation.__args__
        parts = [_python_type_to_str(a) for a in args]
        return " | ".join(parts)

    if annotation is type(None):
        return "None"

    if isinstance(annotation, type):
        return annotation.__name__

    if isinstance(annotation, str):
        return annotation

    return str(annotation)


def _registry_fingerprint(registry) -> str:
    """Compute a stable hash of the registry's param specs for staleness detection."""
    parts = []
    for name in sorted(registry.keys()):
        entry = registry[name]
        sig = inspect.signature(entry.func)
        params = []
        for pname, param in sig.parameters.items():
            if pname in ("song", "ctrl"):
                continue
            ann = _python_type_to_str(param.annotation)
            default = repr(param.default) if param.default is not inspect.Parameter.empty else "REQUIRED"
            params.append(f"{pname}:{ann}={default}")
        parts.append(f"{name}({'|'.join(params)}):{entry.modifying}:{entry.destructive}:{entry.idempotent}")
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()[:16]


def _to_class_name(command_name: str) -> str:
    """Convert command_name to PascalCase class name."""
    return "".join(word.capitalize() for word in command_name.split("_")) + "Params"


def generate() -> str:
    """Generate the shared/commands.py content."""
    registry = get_registry()
    fingerprint = _registry_fingerprint(registry)

    lines = [
        '"""Auto-generated command type definitions.',
        "",
        "Generated from handler function signatures by scripts/generate_command_types.py.",
        'Do not edit manually — regenerate after changing handler signatures.',
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Any, TypedDict",
        "",
        f"REGISTRY_FINGERPRINT = \"{fingerprint}\"",
        "",
        "",
    ]

    # Sort commands by module then name for readability
    commands_by_module: dict[str, list] = {}
    for name, entry in sorted(registry.items()):
        module = entry.func.__module__.rsplit(".", 1)[-1]
        commands_by_module.setdefault(module, []).append((name, entry))

    # Generate TypedDicts
    for module in sorted(commands_by_module.keys()):
        lines.append(f"# {'=' * 60}")
        lines.append(f"# {module}")
        lines.append(f"# {'=' * 60}")
        lines.append("")

        for cmd_name, entry in commands_by_module[module]:
            class_name = _to_class_name(cmd_name)

            if not entry.params:
                lines.append(f"class {class_name}(TypedDict, total=False):")
                lines.append("    pass")
                lines.append("")
                lines.append("")
                continue

            # Determine if all fields have defaults (total=False) or some are required
            has_required = any(default is _SENTINEL for _, default in entry.params)

            if has_required:
                # Split into required and optional
                required = [(p, d) for p, d in entry.params if d is _SENTINEL]
                optional = [(p, d) for p, d in entry.params if d is not _SENTINEL]

                # Get type annotations from the function signature
                sig = inspect.signature(entry.func)

                lines.append(f"class {class_name}(TypedDict, total=False):")
                # Required fields first (marked with Required[] would need Python 3.11+)
                # Since we target 3.11+, we can use total=True for required and NotRequired for optional
                # But simpler: use total=False and document which are required
                for pname, _ in required:
                    param = sig.parameters.get(pname)
                    ann = _python_type_to_str(param.annotation if param else None)
                    lines.append(f"    {pname}: {ann}")
                for pname, default in optional:
                    param = sig.parameters.get(pname)
                    ann = _python_type_to_str(param.annotation if param else None)
                    lines.append(f"    {pname}: {ann}")
                lines.append("")
                lines.append("")
            else:
                sig = inspect.signature(entry.func)
                lines.append(f"class {class_name}(TypedDict, total=False):")
                for pname, default in entry.params:
                    param = sig.parameters.get(pname)
                    ann = _python_type_to_str(param.annotation if param else None)
                    lines.append(f"    {pname}: {ann}")
                lines.append("")
                lines.append("")

    # Generate metadata lookup
    lines.append(f"# {'=' * 60}")
    lines.append("# Command metadata")
    lines.append(f"# {'=' * 60}")
    lines.append("")
    lines.append("COMMAND_TYPES: dict[str, type] = {")
    for cmd_name in sorted(registry.keys()):
        class_name = _to_class_name(cmd_name)
        lines.append(f'    "{cmd_name}": {class_name},')
    lines.append("}")
    lines.append("")
    lines.append("MODIFYING_COMMANDS: frozenset[str] = frozenset({")
    for cmd_name, entry in sorted(registry.items()):
        if entry.modifying:
            lines.append(f'    "{cmd_name}",')
    lines.append("})")
    lines.append("")
    lines.append("READONLY_COMMANDS: frozenset[str] = frozenset({")
    for cmd_name, entry in sorted(registry.items()):
        if not entry.modifying:
            lines.append(f'    "{cmd_name}",')
    lines.append("})")
    lines.append("")

    # Generate annotation overrides (only commands with non-default values)
    lines.append("COMMAND_ANNOTATIONS: dict[str, dict[str, bool]] = {")
    for cmd_name, entry in sorted(registry.items()):
        overrides: dict[str, bool] = {}
        if entry.destructive:
            overrides["destructive"] = True
        if not entry.idempotent:
            overrides["idempotent"] = False
        if overrides:
            pairs = ", ".join(f'"{k}": {v}' for k, v in sorted(overrides.items()))
            lines.append(f'    "{cmd_name}": {{{pairs}}},')
    lines.append("}")
    lines.append("")

    return "\n".join(lines)


def main():
    output = generate()
    out_path = Path(__file__).parent.parent / "shared" / "commands.py"
    out_path.write_text(output)
    print(f"Generated {out_path} ({output.count('class ')} TypedDicts, {output.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
