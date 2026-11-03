# AbletonBridge Cookbook

Escalation reference for when things go wrong or get complex. For basic tool usage and sequencing, read the server instructions (injected on session start). This cookbook covers LOM limitations, workarounds, error diagnosis, and multi-tool patterns for edge cases.

---

## Known LOM Limitations

### Audio tracks and `create_clip`
`create_clip` creates MIDI clips — it fails on audio tracks. Audio tracks need an audio file to create a clip. **Workaround:** Use `load_audio_to_session` with a silent WAV file to create a clip container on an audio track.

### Envelopes on arrangement clips
In Live 12.2.7, `automation_envelope(param)` returned nothing and `create_automation_envelope(param)` was refused ("Not a session clip or parameter belongs to another track") on every arrangement clip tried: MIDI and audio, mixer and device parameters, including a clip duplicated from a session clip with an envelope. So `get_arrangement_automation_hires` reports no automation, and `create_track_automation` fails. **Workaround:** Write on a session clip with `create_clip_automation` or `create_step_automation`, then `duplicate_clip_to_arrangement`, though the copy's envelope can't then be read back through these tools. To copy automation in a saved set, use `als-clone` (`copy_automation`) on the closed file.

### How automation steps behave
A step covers `(start, start + duration]`, and outside its steps an envelope reads as the parameter's own value. `create_clip_automation` therefore holds each value until the next point, and without `append` replaces the whole clip: the first value also covers from the clip's start, and the last holds to its end. With `append` it replaces only from the first point to one `resolution` past the last, so one appended point lasts just that long. Automation tools read just past the requested time, so a step starting there counts.

### `live.remote~` mapping (Envelope Follower, etc.)
M4L device internal mappings (`live.remote~` connections) cannot be created programmatically via LOM. They are internal to the Max patch. **Alternative:** Bake the automation — read a session clip with `get_clip_automation_hires`, write the target with `create_clip_automation`.

**Copying an existing mapping to other sets:** Live saves the mapping in the .als as a LomId link: an `MxDIdRef` in the device points at the LomId of the mapped parameter. `als-clone spec.json` (`als_tools/clone.py`; spec format in `als_tools/spec.py`) copies mapped devices or tracks, and rack-macro automation, from a reference set into closed target sets and re-points the link. The spec can also set a copied device's Max parameters, such as its gain, and add OSC parameters to a plugin in a rack (`osc_params`), mapping each to a macro. Other parameters of that plugin lose their mapping to that macro, other devices on it keep theirs, and existing parameter numbers don't change. Check the result with `als-validate set.als`, then open the set in Live once to confirm.

**Checking that macros reach their destination:** `als-validate` only proves the file is consistent. `als-trace set.als` follows each macro of every rack holding a plugin with a saved OSC list: Max device or automation → macro → plugin parameter → OSC address. It supports Nativize, or any JUCE VST3 saving the same `OSCParameters` list, and does not read other plugins. It exits 1 if a fed macro drives nothing, or if a parameter mapped to it sends no OSC. With `--strict` it also fails when a macro has more than one device mapped to it, or when its name shares nothing with the last part of its OSC address. A clean trace still needs a playback check at the receiver.

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
Extract automation from one parameter, transform, write to another, on session clips:

```
1. get_clip_automation_hires(track_index=A, clip_index=0, parameter_name="Source Param", sample_count=256)
2. Transform the {time, value} points in your code (scale, offset, resample)
3. create_clip_automation(track_index=B, clip_index=0, parameter_name="Target Param", automation_points=[transformed], interpolation="linear")
```

### Hi-Res Automation Sampling
For signal export (WAV rendering, TouchDesigner input):

```
1. get_clip_automation_hires(track_index, clip_index, parameter_name, sample_count=512)
2. Interpolate to your target rate
3. Write to WAV/CSV
```

## Error Diagnosis

**A set won't open, and nothing explains why:** Live may be waiting on a dialog, such as a save prompt, even with its window hidden or the screen locked. `get_live_dialog` shows it, and `press_live_dialog_button` answers it. On the save prompt, in Live 12.2.7, 0 is Don't Save, 1 is Cancel and 2 is Save. Save opens a file panel the tools can't answer, so avoid it unattended.


| Error message | Cause | Fix |
|---|---|---|
| `Unknown command: X` | Remote Script is stale — deployed code has the command but Ableton is running old cached version | Call `reload_remote_script` (deploys + hot-reloads). If that fails, toggle AbletonBridge off/on in Preferences |
| `No clip in slot` | Using a session clip tool (e.g. `get_clip_automation_hires`) but the session slot is empty | Create a clip in the slot first with `create_clip`, or check the slot index |
| `Could not get an automation envelope` | Live gave no envelope on an arrangement clip, which is what it did on every clip tried | Use `create_clip_automation` on a session clip, then `duplicate_clip_to_arrangement` |
| `Clip slot already has a clip` | `create_clip` called on a slot that's occupied | Delete the existing clip first, or use a different slot index |
| `Track X is not an audio track` | `load_audio_to_arrangement`/`load_audio_to_session` called on a MIDI track | These tools require an audio track. Check track type with `get_track_info` |
| `M4L bridge device is not responding` | M4L device not loaded, or UDP connection failed | Load the AbletonBridge M4L device on any track. Check that ports 9878/9879 are not blocked |
| `Connection validation failed` / `Could not connect to Ableton` | MCP server can't reach the Remote Script, or MCP server started before Ableton | Ensure AbletonBridge is selected in Preferences → Link/Tempo & MIDI. Restart the Claude session if the MCP server started before Ableton |
| `Hot-reloaded handlers (0 commands registered)` | Registry cleared but handler modules weren't reimported (pre-fix: string-based sys.modules lookup) | Fixed in `416a34a`. If seen: Cmd+Q Ableton, relaunch to load the fixed hot-reload code |
| TCP timeout on `_reload_handlers` | 18s reload blocking the TCP socket | Fixed in `2fd5c99` (async background thread). If seen: the reload completed but the response timed out — check Ableton log for "commands registered" |
| No AbletonBridge tools in the session / MCP `CONNECTION_CLOSED` | The session launched its own stdio server, which exited because another AbletonBridge instance holds the singleton lock (port 9881). Or the shared SSE server on 9883 is not running | When several sessions need Ableton, run one SSE server (`scripts/start-mcp-server.sh`) and point clients at `{"type": "sse", "url": "http://localhost:9883/sse"}`. `lsof -nP -iTCP:9881 -iTCP:9883 -sTCP:LISTEN` shows which process holds which port. Then reconnect the MCP server in the client |
| None of the above | Unknown or complex issue | Check the Ableton log (`~/Library/Preferences/Ableton/Live <version>/Log.txt`) for the command name and traceback |

---

## Hot-Reload

After changing handler code (Remote Script) or MCP tool code:

```
1. reload_remote_script    — deploys files to Ableton install locations + hot-reloads handlers inside Ableton (no restart needed)
2. reload_tools             — reloads MCP tool modules + sends ToolListChangedNotification so your session picks up new/changed tools
```

Both are MCP tools callable by Claude. The dashboard at `localhost:9880` also has a "Reload Remote Script" button for step 1.

**First time only:** If the hot-reload code itself has never been loaded (fresh Ableton install), one full Ableton restart is needed to load the hot-reload mechanism. After that, no restarts needed.
