# AbletonBridge Refactor Spec

> **Status:** Approved plan — 2026-09-22
> **Scope:** Structural improvements to the Remote Script dispatch and MCP tool surface
> **Goal:** Make extending the tool surface (new tools, new signal types, high-density data) a single-file operation that cannot introduce silent dispatch bugs

---

## Structural Diagnosis

### Where the system breaks down

The callstack has **one weak center and one absent boundary**.

**Weak center: the dispatch table.** 255 hand-written lambdas in `__init__.py` (580 lines). Attention gathers here because every command passes through it, but it resists comprehension — a flat inventory with no organizing logic, no contrast between a zero-param read and a six-param destructive write. It's the structural equivalent of a phone book: comprehensive but illegible.

**Absent boundary: MCP kwargs → handler args.** A typed Python function (`@mcp.tool()`) drops to untyped string keys in a dict, crosses TCP as JSON, and gets unpacked by hand in a lambda (`p.get("track_index", 0)`). A typo in any layer silently produces wrong behavior. There is no mediation zone — no place where the system validates that what left the MCP side is what arrives at the handler.

**Compounding problem: triple-write.** Adding a new tool requires edits in three places that must agree: handler function, MCP tool wrapper, dispatch lambda. The dispatch lambda is the fragile link — it maps parameter names by hand with no validation.

### What's structurally sound

- **`_tool_handler`** — the strongest center. Clean single responsibility (semaphore, timeout, error wrapping). Every MCP tool passes through it. Echoes beautifully across all 16 modules.
- **`AbletonConnection.send_command`** — thick boundary at the TCP layer. Serializes, handles reconnection, parses responses.
- **Handler modules** — well-organized by domain. Functions are small, focused, consistently structured.

---

## The Refactor

Four phases, executed in order. Phases 1-3 are in this PR. Phase 4 is a subagent delegation during this session.

### Phase 1: Dead Code Cleanup ✅

Remove Python 2 compatibility shims. The Remote Script runs on Ableton 11+ (Python 3.11).

- Remove `try: import Queue as queue` → plain `import queue`
- **Risk:** None
- **Status:** Committed

### Phase 2: Extract Knowledge Bases

Move embedded data that isn't handler logic into `MCP_Server/data/`:

| Source | Data | Target | Why |
|---|---|---|---|
| `tools/devices.py` L22-339 | `DEVICE_PROPERTIES` dict (317 lines) | `data/device_properties.json` | Reference data, not logic. Reduces devices.py by 317 lines. Makes the knowledge base editable without touching tool code. |
| `tools/creative.py` (5 locations) | Scale interval definitions | `data/scales.json` | Same dict copy-pasted in 5 functions. DRY violation. |
| `tools/creative.py` L877-921 | Drum pattern templates | `data/drum_patterns.json` | Beat position arrays. Pure data. |

**What stays:** The helper functions in `devices.py` (`_get_property_info`, `_format_property_value`, etc.) remain — they load the JSON and provide the API. The M4L `_build_osc_packet` elif chain stays — it's dispatch logic, not data. Extracting it would create a DSL harder to debug than the elif chain. That's Phase 5 territory (protocol unification), deferred.

- **Risk:** Low. Pure extraction, no behavior change.
- **Verification:** All 214 tests pass.

### Phase 3: Type-Annotate Handler Signatures

Add type annotations and keyword-only argument markers to every public function in all 12 Remote Script handler modules.

**What changes:**

```python
# BEFORE
def create_clip_automation(song, track_index, clip_index, parameter_name,
                           automation_points, device_index=None, append=False, ctrl=None):

# AFTER
def create_clip_automation(
    song,
    track_index: int,
    clip_index: int,
    parameter_name: str,
    automation_points: list,
    *,
    device_index: int | None = None,
    append: bool = False,
    ctrl: 'ControlSurface | None' = None,
) -> dict:
```

**Design decisions:**

- **Type source of truth:** The dispatch lambdas tell us the types — `p.get("track_index", 0)` → `int`, `p.get("name", "")` → `str`. Cross-referenced against the MCP tool signatures which are already fully typed.
- **Keyword-only `*` after `song`:** Functions with 5+ params use `*` to force keyword-only args. This follows the Dignified Python rule and makes the registry dispatch cleaner (everything is `**kwargs`).
- **`Literal` types:** Fixed-value strings use `Literal` — `track_type: Literal["track", "return", "master"]` instead of bare `str`.
- **Return types:** All handlers declare `-> dict` (the standard return shape) or `-> dict | None`.
- **`song` stays untyped:** Ableton's `Song` type isn't importable outside the Live runtime. We annotate it as `song` with no type rather than inventing a protocol.
- **`ctrl` typed as string literal:** `ctrl: 'ControlSurface | None' = None` — forward reference since the type isn't importable in test contexts.

**Delegation:** This is mechanical work across 12 files (~200 functions). Delegated to a subagent with:
- The dispatch table as the type reference
- The MCP tool signatures as cross-reference
- Instructions to apply `*`, `Literal`, and return types

- **Risk:** Low. Additive-only (annotations don't change runtime behavior in Python).
- **Verification:** All tests pass. The registry (Phase 4) can now introspect real types.

### Phase 4: Command Registry

Replace the dispatch table with a self-registering `@command` decorator.

**The mechanism:**

```python
# handlers/_registry.py

_REGISTRY: dict[str, _CommandEntry] = {}

@dataclass
class _CommandEntry:
    func: Callable
    modifying: bool
    params: list[tuple[str, type, Any]]  # (name, annotation, default)

def command(name: str, *, modifying: bool = False):
    """Register a handler function in the command registry."""
    def decorator(func):
        sig = inspect.signature(func)
        params = []
        for pname, param in sig.parameters.items():
            if pname in ('song', 'ctrl'):
                continue
            default = param.default if param.default is not inspect.Parameter.empty else _REQUIRED
            annotation = param.annotation if param.annotation is not inspect.Parameter.empty else Any
            params.append((pname, annotation, default))
        _REGISTRY[name] = _CommandEntry(func=func, modifying=modifying, params=params)
        return func
    return decorator

def dispatch(name: str, song, params_dict: dict, ctrl) -> Any:
    """Dispatch a command by name, unpacking params from the protocol dict."""
    entry = _REGISTRY.get(name)
    if entry is None:
        raise ValueError(f"Unknown command: {name}")
    kwargs = {}
    for pname, _annotation, default in entry.params:
        if default is _REQUIRED:
            kwargs[pname] = params_dict.get(pname)
        else:
            kwargs[pname] = params_dict.get(pname, default)
    return entry.func(song, ctrl=ctrl, **kwargs)

def get_modifying_commands() -> set[str]:
    return {name for name, entry in _REGISTRY.items() if entry.modifying}

def get_readonly_commands() -> set[str]:
    return {name for name, entry in _REGISTRY.items() if not entry.modifying}
```

**What changes in each handler module:**

```python
# handlers/session.py — BEFORE
def set_tempo(song, tempo, ctrl=None):

# handlers/session.py — AFTER
from ._registry import command

@command("set_tempo", modifying=True)
def set_tempo(song, tempo: float, *, ctrl: 'ControlSurface | None' = None) -> dict:
```

**What changes in `__init__.py`:**

The 580-line dispatch table is replaced with:

```python
from .handlers._registry import dispatch, get_modifying_commands, get_readonly_commands

# Force handler module imports so @command decorators run
from .handlers import (
    session, tracks, clips, mixer, devices,
    browser, scenes, arrangement, audio, midi, automation,
)

class AbletonBridge(ControlSurface):
    def _process_command(self, command):
        command_type = command.get("type", "")
        params = command.get("params", {})
        if command_type in get_modifying_commands():
            return self._dispatch_on_main_thread(command_type, params)
        elif command_type in get_readonly_commands():
            return self._dispatch_on_main_thread_readonly(command_type, params)
        else:
            return {"status": "error", "message": f"Unknown command: {command_type}"}

    def _dispatch_modifying(self, cmd, p):
        return dispatch(cmd, self._song, p, self)

    def _dispatch_read_only(self, cmd, p):
        return dispatch(cmd, self._song, p, self)
```

**What stays unchanged:**
- TCP wire protocol (same JSON, same command names, same param names)
- Handler function implementations (only the decorator is added)
- `_tool_handler` on the MCP side
- `reload_tools` functionality
- UDP dispatch path (its own inline dispatch, 2 commands, stays separate)
- The `_process_command` → `_dispatch_on_main_thread` → queue pattern

- **Risk:** Medium. Touches every handler file and replaces the dispatch mechanism.
- **Verification:**
  1. All 214 tests pass
  2. Audit subagent traces 10 representative dispatch paths before/after
  3. Registry entry count matches dispatch table entry count (255 commands)

---

## What's Deferred

| Phase | What | Why deferred |
|---|---|---|
| Shared Command Types | Dataclass schemas shared between MCP and Remote Script | Requires Phase 4 first. Next PR. |
| Tool Naming Convention | `<verb>_<noun>_<qualifier>` normalization | Breaking change for callers. Separate PR with version bump. |
| Protocol Unification | Merge TCP and M4L dispatch into one registry | High risk, requires deep M4L patcher knowledge. Separate effort. |

---

## Post-PR Audit

Four parallel subagents, each with a distinct lens:

### 1. Behavioral Equivalence
Pick 10 tools spanning different modules and dispatch shapes:
- `get_session_info` (read-only, zero params)
- `set_tempo` (modifying, one param)
- `create_clip_automation` (modifying, 6 params, keyword args)
- `get_device_parameters` (read-only, 3 params with track_type)
- `set_device_parameter` (modifying, 5 params)
- `fire_clip` (modifying, 2 params)
- `get_clip_notes` (read-only, 6 params)
- `delete_time` (modifying, destructive, 2 params)
- `set_simpler_properties` (modifying, 20+ optional params)
- `load_browser_item` (modifying, 2 params)

For each: verify the dispatch path produces identical handler invocation (same function, same args, same defaults).

### 2. Alexander Structural Health
Cite specific improvements to:
- **Centers:** Is the registry a stronger center than the dispatch table?
- **Thick boundaries:** Does the decorator create a mediation zone?
- **Levels of scale:** Does the refactor fill the gap between "MCP server" and "tool module"?
- **Echoes:** Does the `@command` pattern echo the `@mcp.tool()` + `@_tool_handler` pattern?
- **Inner calm:** Does `__init__.py` read as simpler despite the same capability?

### 3. Extension Ergonomics
Write a hypothetical new tool `get_track_automation_summary`:
- How many files do you touch?
- Is the process self-evident from the existing patterns?
- Compare before (triple-write) vs after (single decorator).

### 4. Regression Surface
Identify:
- Which tools are most likely to have dispatch mismatches (complex param signatures, keyword-only args, defaults that differ between lambda and function)?
- What could break if `inspect.signature()` produces unexpected results?
- Edge cases: functions with `*args`, `**kwargs`, or params named `song`/`ctrl` that aren't the standard ones.

---

## Success Criteria

After this PR:
1. Adding a new command = one function with `@command` decorator. Done.
2. `__init__.py` is under 200 lines (from 1017).
3. Every handler function has type annotations.
4. All 214 tests pass.
5. The registry entry count matches the old dispatch table (255 commands).
6. The four audit lenses find no behavioral regressions.
