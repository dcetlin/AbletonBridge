# AbletonBridge Cookbook

Agent-facing reference for tool selection, patterns, limitations, and error diagnosis.
Read this resource (`ableton://cookbook`) when you hit a wall or need to choose between tools.

---

## Tool Selection

### Automation: reading

| What you want | Tool | Notes |
|---|---|---|
| Read session clip automation | `get_clip_automation` | 64 fixed samples |
| Read session clip automation (hi-res) | `get_clip_automation_hires` | 2-512 configurable samples |
| Read arrangement automation | `get_arrangement_automation_hires` | 2-512 samples, returns `{beat, value}` with absolute beat positions |
| Read automation states (is param automated?) | `get_automation_states` | M4L tool, returns `automation_state` per param |

### Automation: writing

| What you want | Tool | Notes |
|---|---|---|
| Write to session clip envelope | `create_clip_automation` | Supports `interpolation` (hold/linear/exponential) and per-point overrides |
| Write to arrangement timeline | `create_track_automation` | Needs an arrangement clip covering the time range. See "Audio Track Arrangement Automation" pattern below |
| Write step automation | `create_step_automation` | Held-value steps with explicit durations |
| Generate ADSR envelope | `generate_adsr_automation` | One-call envelope with attack/decay/sustain/release |
| Generate LFO waveform | `generate_lfo_automation` | sine/triangle/saw/square/random with configurable cycles |

### Parameters: reading and writing

| What you want | Tool | Notes |
|---|---|---|
| Get/set a known device parameter | Named commands (`get_device_parameters`, `set_device_parameter`) | Type-safe, validated |
| Explore arbitrary LOM properties | `lom_get` / `lom_set` / `lom_describe` | Generic escape hatch. Path syntax: `tracks[0].devices[1].parameters[3].value` |
| Get/set hidden params (non-automatable) | `discover_device_params` / `set_device_hidden_parameter` | M4L tools, requires M4L bridge device loaded |
| Real-time parameter update (low latency) | UDP tools (`set_parameter_realtime`) | Fire-and-forget, no response |

### Transport layers

| Layer | Port | Use when |
|---|---|---|
| TCP (Remote Script) | 9877 | All standard commands — request/response, 260 commands |
| UDP | 9882 | Real-time parameter updates — fire-and-forget, no confirmation |
| M4L (OSC) | 9878/9879 | Hidden params, deep LOM, audio analysis, chain operations |
| Extensions SDK | HTTP | Device parameter get/set (Apple Silicon only, Live 12.3+) |

---

## Known LOM Limitations

### Arrangement envelope ownership
`automation_envelope(param)` on an arrangement clip requires the parameter object to belong to the same track. Rack macro parameters can fail with "parameter belongs to another track" even when the rack is on the correct track. **Workaround:** Use the session→arrangement pattern (see below).

### First-time arrangement automation
`create_automation_envelope()` does not reliably create envelopes on arrangement clips for parameters that have never been automated. Returns `None`. **Workaround:** Create the envelope on a session clip first (where `create_automation_envelope` works), then `duplicate_clip_to_arrangement`.

### Audio tracks and `create_clip`
`create_clip` creates MIDI clips — it fails on audio tracks. Audio tracks need an audio file to create a clip. **Workaround:** Use `load_audio_to_session` with a silent WAV file to create a clip container on an audio track.

### Mixer parameters on arrangement clips
Volume, Pan, and Send parameters cannot be automated via arrangement clip envelopes. **Workaround:** Use `create_step_automation` on a session clip, then `duplicate_clip_to_arrangement`.

### `live.remote~` mapping (Envelope Follower, etc.)
M4L device internal mappings (`live.remote~` connections) cannot be created programmatically via LOM. They are internal to the Max patch. **Alternative:** Bake the automation — read the source with `get_arrangement_automation_hires`, write to the target with `create_track_automation`.

---

## Multi-Tool Patterns

### Audio Track Arrangement Automation
Write device parameter automation on an audio track's arrangement timeline:

```
1. Generate a silent WAV (or use any audio file as a container)
2. load_audio_to_session(track_index, clip_index=0, file_path="/path/to/silence.wav")
3. create_clip_automation(track_index, clip_index=0, parameter_name="...", automation_points=[...], interpolation="linear")
4. duplicate_clip_to_arrangement(track_index, clip_index=0, time=0.0)
```

### Read → Transform → Write
Extract automation from one parameter, transform, write to another:

```
1. get_arrangement_automation_hires(track_index=A, parameter_name="Source Param", sample_count=256)
2. Transform the {beat, value} points in your code (scale, offset, resample)
3. create_track_automation(track_index=B, parameter_name="Target Param", automation_points=[transformed], interpolation="linear")
```

### Hi-Res Automation Sampling
For signal export (WAV rendering, TouchDesigner input):

```
1. get_arrangement_automation_hires(track_index, parameter_name, sample_count=512)
2. Points are {beat, value} — convert beats to seconds using tempo: seconds = beat * 60 / tempo
3. Resample to target sample rate if needed
```

---

## Error Diagnosis

| Error message | Cause | Fix |
|---|---|---|
| `Unknown command: X` | Remote Script is stale — deployed code has the command but Ableton is running old cached version | Call `reload_remote_script` (deploys + hot-reloads). If that fails, toggle AbletonBridge off/on in Preferences |
| `parameter belongs to another track` | Arrangement clip's `automation_envelope()` rejects the parameter — ownership mismatch with rack macros | Use the session→arrangement pattern instead of writing directly to arrangement clips |
| `No clip in slot` | Using a session clip tool (e.g. `get_clip_automation_hires`) but the session slot is empty — the automation is on the arrangement timeline | Use `get_arrangement_automation_hires` instead |
| `create_arrangement_clip is not available` | Live version doesn't support `track.create_arrangement_clip` | Create the clip manually in Ableton, or use `load_audio_to_arrangement` |
| `Clip does not support automation envelopes` | The clip object doesn't have `automation_envelope` — likely a bare audio clip or incompatible clip type | Try a different clip, or use the session→arrangement pattern |
| `Could not get automation envelope` | `automation_envelope(param)` returned None and `create_automation_envelope` failed | Parameter has never been automated on this clip. Use session clip first (where envelope creation works), then duplicate to arrangement |
| `Clip slot already has a clip` | `create_clip` called on a slot that's occupied | Delete the existing clip first, or use a different slot index |
| `Track X is not an audio track` | `load_audio_to_arrangement`/`load_audio_to_session` called on a MIDI track | These tools require an audio track. Check track type with `get_track_info` |
| `M4L bridge device is not responding` | M4L device not loaded, or UDP connection failed | Load the AbletonBridge M4L device on any track. Check that ports 9878/9879 are not blocked |
| `Connection validation failed` / `Could not connect to Ableton` | MCP server can't reach the Remote Script | Ensure AbletonBridge is selected in Preferences → Link/Tempo & MIDI. Restart the Claude session if the MCP server started before Ableton |

---

## Hot-Reload

After changing handler code (Remote Script) or MCP tool code:

```
1. reload_remote_script    — deploys files to Ableton install locations + hot-reloads handlers inside Ableton (no restart needed)
2. reload_tools             — reloads MCP tool modules + sends ToolListChangedNotification so your session picks up new/changed tools
```

Both are MCP tools callable by Claude. The dashboard at `localhost:9880` also has a "Reload Remote Script" button for step 1.

**First time only:** If the hot-reload code itself has never been loaded (fresh Ableton install), one full Ableton restart is needed to load the hot-reload mechanism. After that, no restarts needed.
