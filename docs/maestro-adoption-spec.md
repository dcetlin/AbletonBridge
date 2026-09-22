# AbletonBridge — Live Maestro Feature Adoption Spec

> **Status:** Light spec — 2026-09-22
> **Source:** [romanstark/live-maestro](https://github.com/romanstark/live-maestro)
> **Scope:** 6 features adopted with attribution, ordered by leverage

---

## 1. Step Budgeting + Time-Budgeted Writes

**Problem:** A 256-beat clip at 0.0625 resolution generates 4,096 steps. Writing these inline blocks Ableton's main thread — the UI freezes, the TCP socket times out, and the automation is half-written with no indication of what landed.

**What Maestro does:** Pre-computes step count before touching Live. If count exceeds `MAX_STEPS=4000`, auto-coarsens resolution. The write loop has a 15s wall-clock deadline — if exceeded, returns a partial-write report with the exact beat range that landed.
[Source: `__init__.py:1354-1405`](https://github.com/romanstark/live-maestro/blob/main/live-remote-script/__init__.py#L1354)

**Implementation:**

```python
# handlers/_helpers.py

MAX_AUTOMATION_STEPS = 4000
AUTOMATION_WRITE_BUDGET_SECONDS = 12.0

def budget_automation_steps(points, resolution, max_steps=MAX_AUTOMATION_STEPS):
    """Auto-coarsen resolution if step count would exceed budget."""
    total_time = max(p["time"] for p in points) - min(p["time"] for p in points)
    step_count = int(total_time / resolution)
    if step_count <= max_steps:
        return resolution, step_count
    coarsened = total_time / max_steps
    return coarsened, max_steps
```

```python
# handlers/automation.py — in create_clip_automation / create_track_automation

import time as _time

resolution, planned_steps = budget_automation_steps(automation_points, resolution)
if interpolation != "hold":
    automation_points = interpolate_automation(automation_points, resolution, interpolation)

deadline = _time.time() + AUTOMATION_WRITE_BUDGET_SECONDS
written = 0
for point in automation_points:
    if _time.time() > deadline:
        break
    envelope.insert_step(time_val, 0.001, clamped)
    written += 1

return {
    "points_added": written,
    "points_planned": len(automation_points),
    "partial": written < len(automation_points),
    "resolution_used": resolution,
}
```

**Files changed:** `_helpers.py`, `automation.py`
**Risk:** Low — additive. Existing behavior unchanged when step count < 4000.

---

## 2. Generic LOM Access (`lom_get`, `lom_set`, `lom_describe`)

**Problem:** 257 named commands cover common operations but not the long tail. An unknown VST parameter, a specific mixer routing property, or a new Live 12 feature — all require a new handler + restart.

**What Maestro does:** Three generic handlers resolve any LOM path at runtime: `lom_get("song.tracks[0].devices[1].parameters[3].value")`. `lom_describe` introspects any object's properties and methods.
[Source: `__init__.py:2226-2257`](https://github.com/romanstark/live-maestro/blob/main/live-remote-script/__init__.py#L2226)

**Implementation:**

```python
# handlers/lom.py (new file)

@command("lom_get")
def lom_get(song, path: str, ctrl=None) -> dict:
    """Resolve a LOM path and return its value."""
    obj = _resolve_path(song, path)
    return {"path": path, "value": _serialize(obj)}

@command("lom_set", modifying=True)
def lom_set(song, path: str, value, ctrl=None) -> dict:
    """Set a LOM property by path."""
    parent, attr = _resolve_parent(song, path)
    setattr(parent, attr, value)
    return {"path": path, "value": getattr(parent, attr)}

@command("lom_describe")
def lom_describe(song, path: str, depth: int = 1, ctrl=None) -> dict:
    """Introspect a LOM object's properties, children, and methods."""
    obj = _resolve_path(song, path)
    return _describe(obj, depth)
```

The path resolver parses dot-separated segments with optional `[index]` notation. A property allowlist prevents writes to dangerous paths.

**Files changed:** New `handlers/lom.py`, update `handlers/__init__.py`
**Risk:** Medium — generic set needs a safety allowlist. Read-only introspection is safe.

---

## 3. Per-Point Interpolation

**Problem:** Our `interpolation` param is curve-global — an entire automation curve uses the same mode. Real automation needs linear ramps that ease into holds, or exponential attacks followed by linear decays.

**What Maestro does:** Each point can override the curve's default interpolation and exponent.
[Source: `automation.py:260-295`](https://github.com/romanstark/live-maestro/blob/main/src/live_maestro/automation.py#L260)

**Implementation:**

Extend the point format from `{time, value}` to `{time, value, interpolation?, exponent?}`:

```python
# _helpers.py — update interpolate_automation

for i in range(len(sorted_pts) - 1):
    t0, v0 = sorted_pts[i]["time"], sorted_pts[i]["value"]
    t1, v1 = sorted_pts[i+1]["time"], sorted_pts[i+1]["value"]
    # Per-point override
    seg_mode = sorted_pts[i].get("interpolation", mode)
    seg_exp = sorted_pts[i].get("exponent", 3.0)
    ...
```

Also add `ease_in` and `ease_out` modes (2 lines each in the interpolation branch).

**Files changed:** `_helpers.py`
**Risk:** None — backward compatible. Points without `interpolation` key use the curve default.

---

## 4. Tool Annotations (4-Tier Command Taxonomy)

**Problem:** `modifying: bool` collapses meaningful distinctions. `create_midi_track` (creates new state) and `delete_track` (destroys state) are both "modifying." MCP supports richer annotations: `readOnlyHint`, `destructiveHint`, `idempotentHint`.

**What Maestro does:** Every tool has MCP `ToolAnnotations`.
[Source: `server.py:1280`](https://github.com/romanstark/live-maestro/blob/main/src/live_maestro/server.py#L1280)

**Implementation:**

```python
# _registry.py — extend @command

def command(name, *, modifying=False, destructive=False, idempotent=True):
    ...

# handlers/automation.py
@command("delete_time", modifying=True, destructive=True, idempotent=False)
```

The MCP tool wrappers can then set `ToolAnnotations` from the registry metadata.

**Files changed:** `_registry.py`, handler files (add flags to destructive commands)
**Risk:** None — additive. Default behavior unchanged.

---

## 5. ADSR + LFO Curve Builders

**Problem:** Building an amplitude envelope or a filter LFO requires manually computing breakpoints. Tedious and error-prone.

**What Maestro does:** `adsr(attack, decay, sustain, release)` and `lfo(shape, beats, cycles)` generate breakpoint lists.
[Source: `automation.py:620`](https://github.com/romanstark/live-maestro/blob/main/src/live_maestro/automation.py#L620), [`automation.py:693`](https://github.com/romanstark/live-maestro/blob/main/src/live_maestro/automation.py#L693)

**Implementation:**

New MCP tools (client-side, no handler changes):

```python
# MCP_Server/tools/automation.py

@mcp.tool()
def generate_adsr_automation(ctx, track_index, clip_index, parameter_name,
                              attack, decay, sustain_level, release,
                              peak=1.0, sustain_time=None):
    """Generate ADSR envelope automation."""
    points = _build_adsr(attack, decay, sustain_level, release, peak, sustain_time)
    return create_clip_automation(ctx, track_index, clip_index, parameter_name,
                                  points, interpolation="exponential")

@mcp.tool()
def generate_lfo_automation(ctx, track_index, clip_index, parameter_name,
                              shape, beats, cycles, min_val=0.0, max_val=1.0):
    """Generate LFO waveform automation (sine, triangle, saw, square)."""
    points = _build_lfo(shape, beats, cycles, min_val, max_val)
    return create_clip_automation(ctx, track_index, clip_index, parameter_name,
                                  points, interpolation="linear")
```

**Files changed:** `MCP_Server/tools/automation.py`
**Risk:** None — pure client-side computation. Uses existing `create_clip_automation`.

---

## 6. Filter Hz↔Normalized Conversion

**Problem:** Ableton's filter frequency is a normalized 0–1 value. Users think in Hz (20–20,000). Without conversion, you're guessing what 0.37 means.

**What Maestro does:** Logarithmic conversion calibrated against real measurements.
[Source: `automation.py:1482-1524`](https://github.com/romanstark/live-maestro/blob/main/src/live_maestro/automation.py#L1482)

**Implementation:**

```python
# MCP_Server/validation.py

import math

_FREQ_MIN = 20.0
_FREQ_MAX = 20000.0

def hz_to_normalized(hz: float) -> float:
    return math.log(hz / _FREQ_MIN) / math.log(_FREQ_MAX / _FREQ_MIN)

def normalized_to_hz(normalized: float) -> float:
    return _FREQ_MIN * (_FREQ_MAX / _FREQ_MIN) ** normalized
```

**Files changed:** `validation.py`
**Risk:** None — utility functions, no behavior change.

---

## 7. Read-Back Verification

**Problem:** After writing automation, we report "Created automation with N points" but never verify that Live actually stored them. Clamping, rounding, or LOM silent failures mean the written data may differ from what was intended.

**What Maestro does:** `compare(expected, actual)` evaluates the expected curve at the actual sample timestamps. Returns verdicts: `MATCH` (median error < epsilon), `DRIFT` (systematic offset), `MISMATCH` (large errors), `FLAT` (all same value — write failed silently), `MISSING` (no envelope). Reports median/max error and worst sample.
[Source: `automation.py:1253-1384`](https://github.com/romanstark/live-maestro/blob/main/src/live_maestro/automation.py#L1253)

**Implementation:**

```python
# _helpers.py

def verify_automation(envelope, expected_points, param_min, param_max, epsilon=0.01):
    """Read back an automation envelope and compare to expected values."""
    errors = []
    for point in expected_points:
        actual = envelope.value_at_time(float(point["time"]))
        expected = max(param_min, min(param_max, float(point["value"])))
        errors.append(abs(actual - expected))
    median_err = sorted(errors)[len(errors) // 2] if errors else 0
    max_err = max(errors) if errors else 0
    if max_err < epsilon:
        return {"verdict": "match", "median_error": median_err, "max_error": max_err}
    elif median_err < epsilon:
        return {"verdict": "drift", "median_error": median_err, "max_error": max_err}
    else:
        return {"verdict": "mismatch", "median_error": median_err, "max_error": max_err}
```

Add optional `verify=False` param to `create_clip_automation` / `create_track_automation`. When True, reads back and includes verdict in the response.

**Files changed:** `_helpers.py`, `automation.py`
**Risk:** None — opt-in. Read-back adds ~50ms per call.

---

## 8. DeferredReadBack

**Problem:** After a write, our handlers return the value they set — not what Live actually stored. If Live clamps, rounds, or rejects the value, we report success with wrong data.

**What Maestro does:** After a write, schedules a second read one tick later via `schedule_message(1, read_task)`. The deferred read captures Live's post-commit state.
[Source: `__init__.py:588-663`](https://github.com/romanstark/live-maestro/blob/main/live-remote-script/__init__.py#L588)

**Implementation:**

```python
# __init__.py — in _dispatch_on_main_thread_impl

def main_thread_task():
    result = dispatch(command_type, self._song, params, self)
    if deferred_read:
        # Schedule a follow-up read after Live processes the write
        def read_back():
            actual = dispatch(deferred_read, self._song, read_params, self)
            result["_verified"] = actual
            response_queue.put({"status": "success", "result": result})
        self.schedule_message(1, read_back)
    else:
        response_queue.put({"status": "success", "result": result})
```

**Files changed:** `__init__.py`
**Risk:** Low — adds one scheduling tick latency for verified writes. Opt-in.

---

## 9. Typed Error Codes

**Problem:** `_safe_error_message` strips useful info from errors. A `TypeError` from a deep LOM call becomes the generic "Invalid parameter type: ..." with no indication of which parameter or what the actual type was. No structured error codes for programmatic handling.

**What Maestro does:** Typed error classes (`LiveCommandError`, `LiveTimeoutError`, `LiveConnectionError`) with structured fields: `code` (e.g., `"index_out_of_range"`, `"bad_path"`, `"unknown_handler"`), `message`, `path`. Timeouts include `may_have_landed: bool` indicating whether the write might have partially succeeded.
[Source: `client.py error classes`](https://github.com/romanstark/live-maestro/blob/main/src/live_maestro/client.py)

**Implementation:**

Replace `_safe_error_message` string mapping with structured error responses:

```python
# __init__.py

def _structured_error(self, e, command_type=None):
    """Return a structured error dict with code and message."""
    if isinstance(e, ValueError):
        code = "invalid_input"
    elif isinstance(e, IndexError):
        code = "index_out_of_range"
    elif isinstance(e, KeyError):
        code = "missing_parameter"
    elif isinstance(e, TypeError):
        code = "type_error"
    elif isinstance(e, queue.Empty):
        code = "timeout"
    elif isinstance(e, RuntimeError):
        code = "runtime_error"
    else:
        code = "internal_error"
    return {
        "status": "error",
        "code": code,
        "message": str(e),
        "command": command_type,
    }
```

For timeouts on modifying commands, add `"may_have_landed": True` — the command was scheduled on the main thread but we didn't wait for it to finish.

**Files changed:** `__init__.py`, MCP-side `AbletonConnection` response parsing
**Risk:** Medium — changes the error response format. MCP tools that check `result.get("status") == "error"` still work, but any code parsing the `message` field may need updating.

---

## 10. LOM Path Catalog (YAML)

**Problem:** Adding a new LOM property access requires writing a handler function, adding a `@command` decorator, restarting Ableton. For exploratory work, this is slow.

**What Maestro does:** 1,166 YAML entries across 5 catalog files define every addressable LOM path with access mode (read/write/call), type, range constraints, and verification status. The executor validates params, dispatches via generic `lom_get`/`lom_set`, and runs read-back verification.
[Source: `catalog/10-song.yaml`](https://github.com/romanstark/live-maestro/blob/main/src/live_maestro/catalog/10-song.yaml)

**Implementation:**

This complements feature #2 (generic LOM access) with a safety layer:

```yaml
# data/lom_catalog.yaml
song:
  tempo:
    access: rw
    type: float
    min: 20.0
    max: 999.0
  tracks:
    access: r
    type: collection
    children:
      name:
        access: rw
        type: str
      mixer_device.volume.value:
        access: rw
        type: float
        min: 0.0
        max: 1.0
```

The `lom_set` handler validates writes against the catalog before executing. Unknown paths still work via generic access but without validation. The catalog grows incrementally.

**Files changed:** New `data/lom_catalog.yaml`, update `handlers/lom.py`
**Risk:** Low — the catalog is advisory validation, not a hard gate. Unknown paths pass through.

---

## Execution Plan

| Phase | Features | Effort | Dependency |
|---|---|---|---|
| A | Step budgeting + time-budgeted writes (#1) | 1 session | None |
| B | Per-point interpolation + ease_in/out (#3) | 30 min | None |
| C | Generic LOM access (#2) + catalog (#10) | 1 session | None |
| D | Tool annotations (#4) | 30 min | None |
| E | ADSR + LFO builders (#5) | 1 hour | Per-point interpolation |
| F | Hz conversion (#6) | 10 min | None |
| G | Read-back verification (#7) + DeferredReadBack (#8) | 1 session | Step budgeting |
| H | Typed error codes (#9) | 1 session | None |

Phases A–D and F can run in parallel. E depends on B. G depends on A. H is standalone.
