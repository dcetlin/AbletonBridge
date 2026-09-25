# AbletonBridge Cookbook

Escalation reference for when things go wrong or get complex. For basic tool usage and sequencing, read the server instructions (injected on session start). This cookbook covers LOM limitations, workarounds, error diagnosis, and multi-tool patterns for edge cases.

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
| `Could not get automation envelope` | `automation_envelope(param)` returned None and `create_automation_envelope` failed | Parameter has never been automated on this clip. Use session clip first (where envelope creation works), then duplicate to arrangement |
| `Clip slot already has a clip` | `create_clip` called on a slot that's occupied | Delete the existing clip first, or use a different slot index |
| `Track X is not an audio track` | `load_audio_to_arrangement`/`load_audio_to_session` called on a MIDI track | These tools require an audio track. Check track type with `get_track_info` |
| `M4L bridge device is not responding` | M4L device not loaded, or UDP connection failed | Load the AbletonBridge M4L device on any track. Check that ports 9878/9879 are not blocked |
| `Connection validation failed` / `Could not connect to Ableton` | MCP server can't reach the Remote Script, or MCP server started before Ableton | Ensure AbletonBridge is selected in Preferences → Link/Tempo & MIDI. Restart the Claude session if the MCP server started before Ableton |
| `Hot-reloaded handlers (0 commands registered)` | Registry cleared but handler modules weren't reimported (pre-fix: string-based sys.modules lookup) | Fixed in `416a34a`. If seen: Cmd+Q Ableton, relaunch to load the fixed hot-reload code |
| TCP timeout on `_reload_handlers` | 18s reload blocking the TCP socket | Fixed in `2fd5c99` (async background thread). If seen: the reload completed but the response timed out — check Ableton log for "commands registered" |
| None of the above | Unknown or complex issue | Read this cookbook. If still stuck, ask the advisor: `send_to_thread(target="ableton-advisor", type="question", text="...")` |

---

## Hot-Reload

After changing handler code (Remote Script) or MCP tool code:

```
1. reload_remote_script    — deploys files to Ableton install locations + hot-reloads handlers inside Ableton (no restart needed)
2. reload_tools             — reloads MCP tool modules + sends ToolListChangedNotification so your session picks up new/changed tools
```

Both are MCP tools callable by Claude. The dashboard at `localhost:9880` also has a "Reload Remote Script" button for step 1.

**First time only:** If the hot-reload code itself has never been loaded (fresh Ableton install), one full Ableton restart is needed to load the hot-reload mechanism. After that, no restarts needed.

---

## Getting Help

If you're stuck on an AbletonBridge issue and this cookbook doesn't cover it, ask the advisor:

- **Visible (thread):** `send_to_thread(target="ableton-advisor", type="question", text="...")`
- **Private (whisper):** via Bash: `hydra deliver --session ableton-advisor --message "your question"`

The advisor reads the codebase, checks the Ableton log, and gives concrete answers with file paths and tool call sequences.

**What to ask the advisor:**
- How to do something the best way (not just any way)
- Error diagnosis when the error table above doesn't match
- Feature requests — "I need a tool that does X"
- Whether something is possible with the current LOM/MCP/M4L surface
- Workflow design — weighing approaches for a specific use case
