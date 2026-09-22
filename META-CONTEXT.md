# AbletonBridge Refactor — Session Context

## What This Repo Is

AbletonBridge is an MCP server that gives Claude agents structural control over Ableton Live — creating tracks, writing MIDI, automating parameters, browsing instruments, analyzing audio. 359 tools across 16 modules. Three transport layers: TCP (Remote Script), UDP/OSC (Max for Live), and HTTP (dashboard).

## Why We're Refactoring

We're building a music-to-visual pipeline (Soulrise project) that writes high-density automation data (pitch contours, envelope curves — 2000+ breakpoints) into Ableton and routes it to TouchDesigner. The current architecture has structural issues that make extending the tool surface error-prone and the automation path fragile.

We just shipped a PR (merged to main) that fixed the immediate blockers: raised automation point caps, added arrangement clip auto-creation, device-scoped parameter lookup, append mode, silent failure detection, and a `reload_tools` hot-reload tool. Those are tactical fixes. This refactor is the structural cleanup.

## The Spec

Read `docs/refactor-spec.md` — it contains:
- 4 Mermaid topology diagrams of the current callstack
- Alexander's 15 principles analysis (strong centers, thick boundaries, interlock, etc.)
- 6-phase refactor plan with recommended ordering
- Specific code examples for the command registry pattern

## What to Execute

**Phase 6 first** (dead code cleanup — zero risk), then **Phase 3** (extract knowledge bases — low risk), then **Phase 1** (command registry — the big one).

Phases 2, 4, 5 are deferred — don't attempt them in this session.

## Constraints

- All existing tests must pass (`uv run pytest tests/`)
- Don't change the TCP wire protocol between MCP server and Remote Script
- Don't touch the M4L Device (Max patcher)
- Don't restructure the MCP server entry point (server.py) beyond what Phase 1 requires
- The `reload_tools` tool must still work after refactoring
- Commit style: `feat:` / `fix:` / `refactor:` prefixes, short descriptions

## Review Lenses

After producing the PR, audit it under these lenses using subagents:

1. **Behavioral equivalence** — do the refactored tools produce identical outputs for identical inputs? Pick 10 representative tools across different modules and verify the dispatch path is equivalent.
2. **Alexander structural health** — does the refactored code exhibit stronger centers, thicker boundaries, and interlock compared to before? Cite specific structural improvements.
3. **Extension ergonomics** — write a new hypothetical tool (e.g., `get_track_automation_summary`) in the refactored system. How many files do you touch? Is the process self-evident from the patterns?
4. **Regression surface** — what could break? Which tools are most likely to have dispatch mismatches after the registry migration?

## Repo Layout

```
AbletonBridge/
├── MCP_Server/           # Python MCP server (runs as Claude subprocess)
│   ├── server.py         # Entry point, FastMCP instance, lifespan
│   ├── tools/            # 16 tool modules, each with register_tools(mcp)
│   │   ├── _base.py      # _tool_handler decorator (the strong center)
│   │   ├── automation.py  # The tools we just fixed
│   │   └── ...
│   ├── connections/       # TCP (ableton.py) and UDP (m4l.py)
│   ├── validation.py     # Input validation + RDP point reduction
│   └── state.py          # Mutable runtime state
├── AbletonBridge_Remote_Script/  # Runs inside Ableton's Python
│   ├── __init__.py       # 1017 lines — dispatch table + TCP server
│   └── handlers/         # 12 handler modules
├── M4L_Device/           # Max for Live patcher (don't touch)
├── docs/
│   ├── refactor-spec.md  # The full spec with Alexander analysis
│   └── ARCHITECTURE.md   # Existing architecture docs
└── tests/                # Unit tests (mocked Ableton connection)
```

## Key Files to Read First

1. `docs/refactor-spec.md` — the full spec
2. `MCP_Server/tools/_base.py` — the `_tool_handler` pattern (the strong center to preserve)
3. `AbletonBridge_Remote_Script/__init__.py` — the 1017-line monolith to replace
4. `AbletonBridge_Remote_Script/handlers/automation.py` — a well-structured handler (reference for the pattern)
5. `MCP_Server/validation.py` — the validation layer
