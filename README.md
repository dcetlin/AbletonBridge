# AbletonBridge

**AI-to-Ableton Live integration through the Model Context Protocol.**

AbletonBridge gives Claude (or any MCP client) direct control over Ableton Live sessions — 353 MCP tools backed by 262 handler commands via a `@command` registry, three transport layers (TCP, UDP/OSC, HTTP), TypedDict codegen, and structured error responses.

Create tracks, write MIDI, design sounds, mix, automate, browse instruments, navigate deep into device chains and modulation matrices — all through natural language.

---

## Architecture

AbletonBridge is a 3-layer system:

```text
Claude AI  <──MCP──>  MCP Server  <──TCP :9877──>  Remote Script (Control Surface)
                          │         <──UDP :9882──>  (real-time parameter updates)
                          ├──────<──UDP/OSC :9878/9879──>  M4L Bridge (optional)
                          └──────<──HTTP :9880──>  Web Dashboard
```

### Transport layers

Three transport layers connect the MCP Server to Ableton:

| Layer | Ports | Model | Use |
|-------|-------|-------|-----|
| **TCP (Remote Script)** | `:9877` | Command/response, newline-delimited JSON | All 260+ commands — session, tracks, clips, devices, automation |
| | `:9882` | Fire-and-forget UDP | Real-time parameter updates at 50+ Hz (knob sweeps, faders) |
| **UDP/OSC (M4L)** | `:9878`/`:9879` | Chunked, base64-encoded | Hidden parameters, rack internals, audio analysis, modulation matrices |
| **HTTP (Dashboard)** | `:9880` | Polling (3s) | Web dashboard — tool metrics, server logs, connection status |

### Command taxonomy

The `@command` registry on the Remote Script classifies every handler:

| Property | Values | Purpose |
|----------|--------|---------|
| `modifying` | `True`/`False` | Write vs. read — controls dispatch delay tier |
| `destructive` | `True`/`False` | Irreversible (delete, remove) — affects retry policy |
| `idempotent` | `True`/`False` | Safe to retry — non-idempotent commands get `max_attempts=1` |

Modifying commands are further bucketed into delay tiers (0 ms / 10 ms / 20 ms) based on how much settling time Ableton needs after the operation.

### Module structure

```text
MCP_Server/                          Remote Script/
├── server.py        (orchestrator)  ├── __init__.py    (Control Surface + dispatch)
├── state.py         (global state)  └── handlers/
├── constants.py     (tiers, limits)     ├── _registry.py  (@command decorator)
├── validation.py    (input guards)      ├── _helpers.py   (shared utilities)
├── instructions.py  (server guidance)   ├── session.py    (65 commands)
├── connections/     (TCP, M4L)          ├── clips.py      (47 commands)
├── cache/           (browser, disk)     ├── devices.py    (35 commands)
├── dashboard/       (Starlette)         ├── tracks.py     (29 commands)
├── tools/           (17 modules)        ├── mixer.py      (23 commands)
│   ├── session.py   (56 tools)          ├── automation.py (14 commands)
│   ├── clips.py     (54 tools)          ├── browser.py    (12 commands)
│   ├── devices.py   (44 tools)          ├── scenes.py     (10 commands)
│   ├── m4l_tools.py (40 tools)          ├── midi.py       (9 commands)
│   ├── ...          (17 total)          ├── audio.py      (7 commands)
│   └── lom.py       (3 tools)          ├── arrangement.py(6 commands)
│                                        └── lom.py        (3 commands)
└── prompts.py       (4 workflows)
```

### Architecture diagrams

Six Mermaid diagrams in [`diagrams/`](diagrams/) cover the system in detail:

1. [Deployment topology](diagrams/1-deployment-topology.png) — layers, ports, protocols
2. [Command dispatch flow](diagrams/2-command-dispatch-flow.png) — TCP dispatch through the `@command` registry
3. [UDP real-time flow](diagrams/3-udp-realtime-flow.png) — fire-and-forget parameter path
4. [Codegen pipeline](diagrams/4-codegen-pipeline.png) — `@command` → TypedDict → fingerprint test
5. [M4L bridge flow](diagrams/5-m4l-bridge-flow.png) — OSC chunked protocol
6. [Error boundary layers](diagrams/6-error-boundary-layers.png) — structured error classification

---

## Key Features

- **262 handler commands** via `@command` registry with introspected param specs, TypedDict codegen, and fingerprint-based staleness detection
- **353 MCP tools** across 17 modules — session, tracks, clips, mixer, devices, browser, automation, arrangement, scenes, creative generation, M4L deep access, snapshots, audio, grid notation, MIDI CC, LOM, and compound workflows
- **Generic LOM access** — `lom_get`, `lom_set`, `lom_describe` for arbitrary Live Object Model traversal with path resolution, depth-bounded introspection, and a write denylist
- **Per-point interpolation** — automation commands accept per-point `interpolation` overrides (linear/hold/custom exponent) with configurable resolution
- **Step-budgeted automation** — `_reduce_automation_points` with collinear-point elimination keeps large automation writes within Ableton's dispatch timeout
- **Structured error responses** — Remote Script `_structured_error` classifies exceptions into 9 codes (`invalid_input`, `index_out_of_range`, `missing_parameter`, `type_error`, `attribute_error`, `not_implemented`, `runtime_error`, `timeout`, `internal_error`) with optional `may_have_landed` flag for non-idempotent failures
- **3-layer transport** — TCP for commands + UDP for real-time parameters (Remote Script), UDP/OSC for M4L deep access, HTTP for dashboard
- **MIDI CC control** — 100 built-in CC maps for Arturia V Collection and NI Komplete via virtual MIDI port
- **Chunked async responses** — large payloads split, base64-encoded, reassembled with duplicate detection and missing-chunk reporting
- **Tiered command delays** — 3-tier system (0 / 10 / 20 ms) with `asyncio.Semaphore(1)` serialization replacing large defensive delays
- **Disk-persisted browser cache** — 6,400+ items in gzip, ~50 ms startup
- **CI via GitHub Actions** — pytest on Python 3.12 + 3.14, pyright type-checking with ratcheted error baseline

---

## Installation

### Prerequisites

- Python 3.10+
- Ableton Live 10, 11, or 12
- Any MCP client (Claude Desktop, Cursor, Claude Code)

### Setup

1. **Install the MCP server:**

   ```bash
   pip install -e .
   ```

2. **Install the Remote Script:**

   Copy `AbletonBridge_Remote_Script/` to your Ableton MIDI Remote Scripts folder:
   - **macOS:** `~/Music/Ableton/User Library/Remote Scripts/`
   - **Windows:** `~\Documents\Ableton\User Library\Remote Scripts\`

   Enable it in Ableton → Preferences → Link, Tempo & MIDI → Control Surface.

3. **Install the M4L Bridge (optional):**

   Drop `AbletonBridge_M4L/AbletonBridge.amxd` onto any track as an Audio Effect.

4. **Add to your MCP client config:**

   ```json
   {
     "mcpServers": {
       "ableton-bridge": {
         "command": "uv",
         "args": ["run", "--directory", "/path/to/AbletonBridge", "python", "-m", "MCP_Server"]
       }
     }
   }
   ```

### Optional: ElevenLabs Voice & SFX

19 additional tools for AI voice generation, sound effects, and cloning. Requires `ELEVENLABS_API_KEY`.

```json
{
  "elevenlabs": {
    "command": "uv",
    "args": ["run", "elevenlabs-mcp"],
    "env": { "ELEVENLABS_API_KEY": "your_key_here" }
  }
}
```

### Optional: MIDI CC Plugin Control

For direct CC control of plugin parameters (Arturia V Collection, NI Komplete):

```bash
pip install -e ".[midi_cc]"
```

---

## Usage

**Music creation** — *"Create a MIDI track, load Operator, and write an 8-bar bass line in E minor"*

**Sound design** — *"Load Wavetable and design a warm detuned supersaw pad"*

**Deep device access** — *"Show me what's inside the Drum Rack — all chains and nested devices"*

**Mixing** — *"Create a filter sweep automation from 0.2 to 0.9 over 8 bars with linear interpolation"*

**Generic LOM** — *"Use lom_describe on tracks[0].devices[0] at depth 2 to explore its properties"*

**Creative generation** — *"Generate a Euclidean rhythm with 16 steps and 5 pulses"*

### MCP Resources

- `ableton://session` — current session state
- `ableton://tracks` — all track information
- `ableton://capabilities` — server version, connections, cache status

### MCP Prompts

Guided workflows: `create-beat`, `mix-track`, `sound-design`, `arrange-section`.

---

## Development

### Running tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -x -q
```

342 tests across 18 test files covering validation, connections, M4L, browser cache, creative tools, workflows, registry consistency, error codes, LOM, automation pipeline, annotations, read-back verification, and curve builders.

### Regenerating TypedDicts

After changing handler function signatures:

```bash
python scripts/generate_command_types.py
```

This updates `shared/commands.py` (260 TypedDicts, ~2000 lines) from the `@command` registry. The registry fingerprint test (`test_registry.py`) will fail if the generated file is stale.

### Type checking

```bash
pip install pyright==1.1.400
pyright
```

CI enforces a ratcheted error baseline (currently 195).

### Project structure

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full module dependency graph, communication protocols, and design decisions.

---

## Compatibility

- **Ableton Live 10, 11, 12** — graceful API fallbacks for version-specific features
- **macOS and Windows**
- **Any MCP client** — Claude Desktop, Cursor, Claude Code, or any MCP-compatible tool
- **Python 3.10+** — CI tests on 3.12 and 3.14

---

## Version

**v4.0.0** — see [CHANGELOG.md](CHANGELOG.md) for full release history.

---

## Attribution

Built on the original [AbletonBridge](https://github.com/hidingwill/AbletonBridge) by William De Simone ([@hidingwill](https://github.com/hidingwill)). Step-budgeted automation, per-point interpolation, and generic LOM access patterns adapted from [Live Maestro](https://github.com/romanstark/live-maestro) by Roman Stark.

Licensed under MIT.
