"""Session-level commands: tempo, playback, transport, loop, recording, metronome."""

from __future__ import absolute_import, print_function, unicode_literals

from ._helpers import get_track, get_clip
from ._registry import command


@command("get_session_info")
def get_session_info(song, ctrl=None) -> dict:
    """Get information about the current session."""
    result = {
        "tempo": song.tempo,
        "signature_numerator": song.signature_numerator,
        "signature_denominator": song.signature_denominator,
        "track_count": len(song.tracks),
        "return_track_count": len(song.return_tracks),
        "master_track": {
            "name": "Master",
            "volume": song.master_track.mixer_device.volume.value,
            "panning": song.master_track.mixer_device.panning.value,
        },
    }
    return result


@command("set_tempo", modifying=True)
def set_tempo(song, tempo: float, ctrl=None) -> dict:
    """Set the tempo of the session (20.0-999.0 BPM)."""
    tempo = float(tempo)
    if tempo < 20.0 or tempo > 999.0:
        raise ValueError(
            "Tempo must be between 20.0 and 999.0 BPM, got {0}".format(tempo))
    song.tempo = tempo
    return {"tempo": song.tempo}


@command("start_playback", modifying=True)
def start_playback(song, ctrl=None) -> dict:
    """Start playing the session."""
    song.start_playing()
    return {"playing": song.is_playing}


@command("stop_playback", modifying=True)
def stop_playback(song, ctrl=None) -> dict:
    """Stop playing the session."""
    song.stop_playing()
    return {"playing": song.is_playing}


@command("get_song_transport")
def get_song_transport(song, ctrl=None) -> dict:
    """Get transport/arrangement state."""
    result = {
        "current_time": song.current_song_time,
        "is_playing": song.is_playing,
        "tempo": song.tempo,
        "signature_numerator": song.signature_numerator,
        "signature_denominator": song.signature_denominator,
        "loop_enabled": song.loop,
        "loop_start": song.loop_start,
        "loop_length": song.loop_length,
        "song_length": song.song_length,
    }
    try:
        result["record_mode"] = song.record_mode
    except Exception:
        result["record_mode"] = False
    try:
        result["punch_in"] = song.punch_in
    except Exception:
        result["punch_in"] = None
    try:
        result["punch_out"] = song.punch_out
    except Exception:
        result["punch_out"] = None
    try:
        result["count_in_duration"] = int(song.count_in_duration)
    except Exception:
        result["count_in_duration"] = None
    try:
        result["is_counting_in"] = song.is_counting_in
    except Exception:
        result["is_counting_in"] = None
    return result


@command("set_song_time", modifying=True)
def set_song_time(song, time: float, ctrl=None) -> dict:
    """Set the arrangement playhead position."""
    target = max(0.0, float(time))
    song.current_song_time = target
    return {"current_time": target}


@command("set_song_loop", modifying=True)
def set_song_loop(song, enabled: bool = None, start: float = None, length: float = None, ctrl=None) -> dict:
    """Control arrangement loop bracket."""
        # Validate all inputs before mutating
    v_enabled = None
    v_start = None
    v_length = None
    if enabled is not None:
        v_enabled = bool(enabled)
    if start is not None:
        v_start = max(0.0, float(start))
    if length is not None:
        v_length = float(length)
        if v_length <= 0:
            raise ValueError("Loop length must be positive, got {0}".format(v_length))

    # Apply validated values
    if v_enabled is not None:
        song.loop = v_enabled
    if v_start is not None:
        song.loop_start = v_start
    if v_length is not None:
        song.loop_length = v_length

    return {
        "loop_enabled": v_enabled if v_enabled is not None else song.loop,
        "loop_start": v_start if v_start is not None else song.loop_start,
        "loop_length": v_length if v_length is not None else song.loop_length,
    }


# --- New commands from MacWhite ---


@command("get_loop_info")
def get_loop_info(song, ctrl=None) -> dict:
    """Get loop information."""
    return {
        "loop_start": song.loop_start,
        "loop_end": song.loop_start + song.loop_length,
        "loop_length": song.loop_length,
        "loop": song.loop,
        "current_song_time": song.current_song_time,
    }


@command("set_loop_start", modifying=True)
def set_loop_start(song, position: float, ctrl=None) -> dict:
    """Set the loop start position."""
    position = max(0.0, float(position))
    song.loop_start = position
    return {"loop_start": song.loop_start, "loop_end": song.loop_start + song.loop_length}


@command("set_loop_end", modifying=True)
def set_loop_end(song, position: float, ctrl=None) -> dict:
    """Set the loop end position."""
    pos = float(position)
    if pos <= song.loop_start:
        raise ValueError("Loop end ({0}) must be greater than loop start ({1})".format(
            pos, song.loop_start))
    # loop_end isn't a direct property; compute via loop_length
    song.loop_length = pos - song.loop_start
    return {"loop_start": song.loop_start, "loop_end": song.loop_start + song.loop_length}


@command("set_loop_length", modifying=True)
def set_loop_length(song, length: float, ctrl=None) -> dict:
    """Set the loop length."""
    length_val = float(length)
    if length_val <= 0:
        raise ValueError("Loop length must be positive, got {0}".format(length_val))
    song.loop_length = length_val
    return {
        "loop_start": song.loop_start,
        "loop_end": song.loop_start + song.loop_length,
        "loop_length": song.loop_length,
    }


@command("set_playback_position", modifying=True)
def set_playback_position(song, position: float, ctrl=None) -> dict:
    """Set the playback position."""
    song.current_song_time = max(0.0, float(position))
    return {"current_song_time": song.current_song_time}


@command("set_arrangement_overdub", modifying=True)
def set_arrangement_overdub(song, enabled: bool, ctrl=None) -> dict:
    """Enable or disable arrangement overdub mode."""
    song.arrangement_overdub = bool(enabled)
    return {"arrangement_overdub": song.arrangement_overdub}


@command("start_arrangement_recording", modifying=True)
def start_arrangement_recording(song, ctrl=None) -> dict:
    """Start recording into the arrangement view."""
    song.record_mode = True
    if not song.is_playing:
        song.start_playing()
    return {
        "recording": song.record_mode,
        "playing": song.is_playing,
        "arrangement_overdub": song.arrangement_overdub,
    }


@command("stop_arrangement_recording", modifying=True)
def stop_arrangement_recording(song, stop_playback: bool = True, ctrl=None) -> dict:
    """Stop arrangement recording.

    Args:
        song: Live Song object.
        stop_playback: If True (default), also stops transport playback.
            Set to False to stop recording while keeping playback running
            (useful for punch-out workflows where you want to keep listening).
        ctrl: Optional controller for logging.
    """
    song.record_mode = False
    if stop_playback and song.is_playing:
        song.stop_playing()
    return {"recording": song.record_mode, "playing": song.is_playing}


@command("get_recording_status")
def get_recording_status(song, ctrl=None) -> dict:
    """Get the current recording status."""
    armed_tracks = []
    for i, track in enumerate(song.tracks):
        try:
            if track.can_be_armed and track.arm:
                armed_tracks.append({
                    "index": i,
                    "name": track.name,
                    "is_midi": track.has_midi_input,
                    "is_audio": track.has_audio_input,
                })
        except Exception:
            pass
    return {
        "record_mode": song.record_mode,
        "arrangement_overdub": song.arrangement_overdub,
        "session_record": song.session_record,
        "is_playing": song.is_playing,
        "armed_tracks": armed_tracks,
        "armed_track_count": len(armed_tracks),
    }


@command("set_metronome", modifying=True)
def set_metronome(song, enabled: bool, ctrl=None) -> dict:
    """Enable or disable the metronome."""
    song.metronome = bool(enabled)
    return {"metronome": song.metronome}


@command("tap_tempo", modifying=True)
def tap_tempo(song, ctrl=None) -> dict:
    """Tap tempo to set BPM."""
    song.tap_tempo()
    return {"tempo": song.tempo}


# --- Undo / Redo ---


@command("undo", modifying=True)
def undo(song, ctrl=None) -> dict:
    """Undo the last action."""
    if not song.can_undo:
        return {"undone": False, "reason": "Nothing to undo"}
    song.undo()
    return {"undone": True}


@command("redo", modifying=True)
def redo(song, ctrl=None) -> dict:
    """Redo the last undone action."""
    if not song.can_redo:
        return {"redone": False, "reason": "Nothing to redo"}
    song.redo()
    return {"redone": True}


# --- Additional transport ---


@command("continue_playing", modifying=True)
def continue_playing(song, ctrl=None) -> dict:
    """Continue playback from the current position (does not jump to start)."""
    song.continue_playing()
    return {"playing": song.is_playing, "position": song.current_song_time}


@command("re_enable_automation", modifying=True)
def re_enable_automation(song, ctrl=None) -> dict:
    """Re-enable all automation that has been manually overridden."""
    song.re_enable_automation()
    return {"re_enabled": True}


# --- Cue points ---


@command("get_cue_points")
def get_cue_points(song, ctrl=None) -> dict:
    """Get all cue points (markers) in the arrangement."""
    cues = []
    for cue in song.cue_points:
        cues.append({
            "name": cue.name,
            "time": cue.time,
        })
    cues.sort(key=lambda c: c["time"])
    return {"cue_points": cues, "count": len(cues)}


@command("set_or_delete_cue", modifying=True)
def set_or_delete_cue(song, ctrl=None) -> dict:
    """Toggle a cue point at the current playback position.

    If a cue point exists at the current position, it is deleted.
    Otherwise, a new cue point is created.
    """
    song.set_or_delete_cue()
    return {"position": song.current_song_time}


@command("jump_to_cue", modifying=True)
def jump_to_cue(song, direction: str, ctrl=None) -> dict:
    """Jump to the next or previous cue point.

    Args:
        direction: 'next' or 'prev'
    """
    if direction == "next":
        if not song.can_jump_to_next_cue:
            return {"jumped": False, "reason": "No next cue point"}
        song.jump_to_next_cue()
    elif direction == "prev":
        if not song.can_jump_to_prev_cue:
            return {"jumped": False, "reason": "No previous cue point"}
        song.jump_to_prev_cue()
    else:
        raise ValueError("direction must be 'next' or 'prev', got '{0}'".format(direction))
    return {"jumped": True, "position": song.current_song_time}


@command("get_groove_pool")
def get_groove_pool(song, ctrl=None) -> dict:
    """Read the groove pool: global groove amount and list of grooves with their params."""
    result = {
        "groove_amount": getattr(song, "groove_amount", 1.0),
        "grooves": [],
    }
    pool = getattr(song, "groove_pool", None)
    if pool is not None and hasattr(pool, "grooves"):
        for i, groove in enumerate(pool.grooves):
            groove_info = {
                "index": i,
                "name": getattr(groove, "name", "Groove {0}".format(i)),
                "timing_amount": getattr(groove, "timing_amount", 0.0),
                "quantization_amount": getattr(groove, "quantization_amount", 0.0),
                "random_amount": getattr(groove, "random_amount", 0.0),
                "velocity_amount": getattr(groove, "velocity_amount", 0.0),
            }
            result["grooves"].append(groove_info)
    result["groove_count"] = len(result["grooves"])
    return result


# --- Song Settings ---


@command("get_song_settings")
def get_song_settings(song, ctrl=None) -> dict:
    """Get global song settings: time signature, swing, quantization, overdub, etc."""
    result = {
        "signature_numerator": song.signature_numerator,
        "signature_denominator": song.signature_denominator,
        "swing_amount": song.swing_amount,
        "arrangement_overdub": song.arrangement_overdub,
        "back_to_arranger": song.back_to_arranger,
    }
    try:
        result["clip_trigger_quantization"] = int(song.clip_trigger_quantization)
    except Exception:
        result["clip_trigger_quantization"] = None
    try:
        result["midi_recording_quantization"] = int(song.midi_recording_quantization)
    except Exception:
        result["midi_recording_quantization"] = None
    try:
        result["follow_song"] = song.view.follow_song
    except Exception:
        result["follow_song"] = None
    try:
        result["draw_mode"] = song.view.draw_mode
    except Exception:
        result["draw_mode"] = None
    try:
        result["tempo_follower_enabled"] = song.tempo_follower_enabled
    except Exception:
        result["tempo_follower_enabled"] = None
    try:
        result["exclusive_arm"] = song.exclusive_arm
    except Exception:
        result["exclusive_arm"] = None
    try:
        result["exclusive_solo"] = song.exclusive_solo
    except Exception:
        result["exclusive_solo"] = None
    try:
        result["session_automation_record"] = song.session_automation_record
    except Exception:
        result["session_automation_record"] = None
    try:
        result["song_length"] = song.song_length
    except Exception:
        result["song_length"] = None
    return result


@command("set_song_settings", modifying=True)
def set_song_settings(song, signature_numerator: int = None, signature_denominator: int = None,
                       swing_amount: float = None, clip_trigger_quantization: int = None,
                       midi_recording_quantization: int = None, back_to_arranger: bool = None,
                       follow_song: bool = None, draw_mode: bool = None,
                       session_automation_record: bool = None, ctrl=None) -> dict:
    """Set global song settings."""
        # Phase 1: validate all inputs into local vars before mutating song
    validated = {}
    if signature_numerator is not None:
        val = int(signature_numerator)
        if val < 1 or val > 99:
            raise ValueError("signature_numerator must be 1-99, got {0}".format(val))
        validated["signature_numerator"] = val
    if signature_denominator is not None:
        val = int(signature_denominator)
        if val not in (1, 2, 4, 8, 16):
            raise ValueError("signature_denominator must be 1, 2, 4, 8, or 16, got {0}".format(val))
        validated["signature_denominator"] = val
    if swing_amount is not None:
        val = float(swing_amount)
        if val < 0.0 or val > 1.0:
            raise ValueError("swing_amount must be 0.0-1.0, got {0}".format(val))
        validated["swing_amount"] = val
    if clip_trigger_quantization is not None:
        val = int(clip_trigger_quantization)
        if val < 0 or val > 13:
            raise ValueError("clip_trigger_quantization must be 0-13 (Live RecordingQuantization enum), got {0}".format(val))
        validated["clip_trigger_quantization"] = val
    if midi_recording_quantization is not None:
        val = int(midi_recording_quantization)
        if val < 0 or val > 13:
            raise ValueError("midi_recording_quantization must be 0-13 (Live RecordingQuantization enum), got {0}".format(val))
        validated["midi_recording_quantization"] = val
    if back_to_arranger is not None:
        validated["back_to_arranger"] = bool(back_to_arranger)
    if follow_song is not None:
        validated["follow_song"] = bool(follow_song)
    if draw_mode is not None:
        validated["draw_mode"] = bool(draw_mode)
    if session_automation_record is not None:
        validated["session_automation_record"] = bool(session_automation_record)
    if not validated:
        raise ValueError("No parameters specified")

    # Phase 2: apply all validated values
    changes = {}
    if "signature_numerator" in validated:
        song.signature_numerator = validated["signature_numerator"]
        changes["signature_numerator"] = validated["signature_numerator"]
    if "signature_denominator" in validated:
        song.signature_denominator = validated["signature_denominator"]
        changes["signature_denominator"] = validated["signature_denominator"]
    if "swing_amount" in validated:
        song.swing_amount = validated["swing_amount"]
        changes["swing_amount"] = validated["swing_amount"]
    if "clip_trigger_quantization" in validated:
        song.clip_trigger_quantization = validated["clip_trigger_quantization"]
        changes["clip_trigger_quantization"] = validated["clip_trigger_quantization"]
    if "midi_recording_quantization" in validated:
        song.midi_recording_quantization = validated["midi_recording_quantization"]
        changes["midi_recording_quantization"] = validated["midi_recording_quantization"]
    if "back_to_arranger" in validated:
        song.back_to_arranger = validated["back_to_arranger"]
        changes["back_to_arranger"] = validated["back_to_arranger"]
    if "follow_song" in validated:
        song.view.follow_song = validated["follow_song"]
        changes["follow_song"] = validated["follow_song"]
    if "draw_mode" in validated:
        song.view.draw_mode = validated["draw_mode"]
        changes["draw_mode"] = validated["draw_mode"]
    if "session_automation_record" in validated:
        song.session_automation_record = validated["session_automation_record"]
        changes["session_automation_record"] = validated["session_automation_record"]
    return changes


# --- Navigation / Transport actions ---


@command("trigger_session_record", modifying=True)
def trigger_session_record(song, record_length: float = None, ctrl=None) -> dict:
    """Trigger a new session recording, optionally with a fixed bar length."""
    if record_length is not None:
        song.trigger_session_record(float(record_length))
    else:
        song.trigger_session_record()
    return {"triggered": True, "record_length": record_length}


@command("navigate_playback", modifying=True)
def navigate_playback(song, action: str, beats: float = None, ctrl=None) -> dict:
    """Navigate playback position: jump_by, scrub_by, or play_selection.

    Args:
        action: 'jump_by', 'scrub_by', or 'play_selection'
        beats: Number of beats to jump/scrub (required for jump_by and scrub_by)
    """
    if action == "jump_by":
        if beats is None:
            raise ValueError("beats is required for jump_by")
        song.jump_by(float(beats))
        return {"action": "jump_by", "beats": float(beats), "position": song.current_song_time}
    elif action == "scrub_by":
        if beats is None:
            raise ValueError("beats is required for scrub_by")
        song.scrub_by(float(beats))
        return {"action": "scrub_by", "beats": float(beats), "position": song.current_song_time}
    elif action == "play_selection":
        song.play_selection()
        return {"action": "play_selection", "position": song.current_song_time}
    else:
        raise ValueError("action must be 'jump_by', 'scrub_by', or 'play_selection', got '{0}'".format(action))


# --- View / Selection ---


@command("select_scene", modifying=True)
def select_scene(song, scene_index: int, ctrl=None) -> dict:
    """Select a scene by index in Live's Session view."""
    scenes = list(song.scenes)
    if scene_index < 0 or scene_index >= len(scenes):
        raise IndexError("Scene index {0} out of range (have {1} scenes)".format(
            scene_index, len(scenes)))
    song.view.selected_scene = scenes[scene_index]
    return {"selected_scene_index": scene_index, "scene_name": scenes[scene_index].name}


@command("select_track", modifying=True)
def select_track(song, track_index: int, track_type: str = "track", ctrl=None) -> dict:
    """Select a track by index in Live's Session or Arrangement view.

    Args:
        track_index: The index of the track.
        track_type: 'track', 'return', or 'master'.
    """
    target = get_track(song, track_index, track_type)
    song.view.selected_track = target
    return {"selected_track": target.name, "track_type": track_type}


@command("set_detail_clip", modifying=True)
def set_detail_clip(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Show a clip in Live's Detail view.

    Args:
        track_index: The track containing the clip.
        clip_index: The clip slot index.
    """
    _, clip = get_clip(song, track_index, clip_index)
    song.view.detail_clip = clip
    return {
        "track_index": track_index,
        "clip_index": clip_index,
        "clip_name": clip.name,
    }


@command("set_groove_settings", modifying=True)
def set_groove_settings(song, groove_amount: float = None, groove_index: int = None,
                         timing_amount: float = None, quantization_amount: float = None,
                         random_amount: float = None, velocity_amount: float = None, ctrl=None) -> dict:
    """Set global groove amount or individual groove parameters."""
    result = {}
    if groove_amount is not None:
        groove_amount = float(groove_amount)
        if groove_amount < 0.0 or groove_amount > 1.0:
            raise ValueError(
                "groove_amount must be between 0.0 and 1.0, got {0}".format(groove_amount))
        song.groove_amount = groove_amount
        result["groove_amount"] = song.groove_amount
    if groove_index is not None:
        pool = getattr(song, "groove_pool", None)
        if pool is None or not hasattr(pool, "grooves"):
            raise RuntimeError("Groove pool not available")
        grooves = list(pool.grooves)
        groove_index = int(groove_index)
        if groove_index < 0 or groove_index >= len(grooves):
            raise IndexError("Groove index {0} out of range (have {1} grooves)".format(
                groove_index, len(grooves)))
        groove = grooves[groove_index]
        if timing_amount is not None:
            val = float(timing_amount)
            if val < 0.0 or val > 1.0:
                raise ValueError("timing_amount must be 0.0-1.0, got {0}".format(val))
            groove.timing_amount = val
        if quantization_amount is not None:
            val = float(quantization_amount)
            if val < 0.0 or val > 1.0:
                raise ValueError("quantization_amount must be 0.0-1.0, got {0}".format(val))
            groove.quantization_amount = val
        if random_amount is not None:
            val = float(random_amount)
            if val < 0.0 or val > 1.0:
                raise ValueError("random_amount must be 0.0-1.0, got {0}".format(val))
            groove.random_amount = val
        if velocity_amount is not None:
            val = float(velocity_amount)
            if val < -1.0 or val > 1.0:
                raise ValueError("velocity_amount must be -1.0-1.0, got {0}".format(val))
            groove.velocity_amount = val
        result["groove_index"] = groove_index
        result["groove_name"] = getattr(groove, "name", "")
        result["timing_amount"] = groove.timing_amount
        result["quantization_amount"] = groove.quantization_amount
        result["random_amount"] = groove.random_amount
        result["velocity_amount"] = groove.velocity_amount
    if not result:
        raise ValueError("No parameters specified")
    return result


# --- Scale & Root Note ---


@command("get_song_scale")
def get_song_scale(song, ctrl=None) -> dict:
    """Get the song's current scale settings (root note, scale name, mode, intervals)."""
    result = {
        "root_note": song.root_note,
        "scale_name": song.scale_name,
        "scale_mode": song.scale_mode,
    }
    try:
        result["scale_intervals"] = list(song.scale_intervals)
    except Exception:
        result["scale_intervals"] = None
    return result


@command("set_song_scale", modifying=True)
def set_song_scale(song, root_note: int = None, scale_name: str = None, scale_mode: bool = None, ctrl=None) -> dict:
    """Set the song's scale settings.

    Args:
        root_note: 0-11 (C=0, C#=1, ..., B=11)
        scale_name: Scale name as shown in Live (e.g. 'Major', 'Minor', 'Dorian')
        scale_mode: True to enable Scale Mode highlighting
    """
    changes = {}
    if root_note is not None:
        val = int(root_note)
        if val < 0 or val > 11:
            raise ValueError("root_note must be 0-11, got {0}".format(val))
        song.root_note = val
        changes["root_note"] = val
    if scale_name is not None:
        song.scale_name = str(scale_name)
        changes["scale_name"] = song.scale_name
    if scale_mode is not None:
        song.scale_mode = bool(scale_mode)
        changes["scale_mode"] = bool(scale_mode)
    if not changes:
        raise ValueError("No parameters specified")
    return changes


# --- Punch In/Out ---


@command("set_punch", modifying=True)
def set_punch(song, punch_in: bool = None, punch_out: bool = None, count_in_duration: int = None, ctrl=None) -> dict:
    """Set punch in/out and count-in settings.

    Args:
        punch_in: Enable/disable punch-in
        punch_out: Enable/disable punch-out
        count_in_duration: 0=None, 1=1 Bar, 2=2 Bars, 3=4 Bars
    """
    changes = {}
    if punch_in is not None:
        song.punch_in = bool(punch_in)
        changes["punch_in"] = bool(punch_in)
    if punch_out is not None:
        song.punch_out = bool(punch_out)
        changes["punch_out"] = bool(punch_out)
    if count_in_duration is not None:
        val = int(count_in_duration)
        if val < 0 or val > 3:
            raise ValueError("count_in_duration must be 0-3, got {0}".format(val))
        try:
            song.count_in_duration = val
            changes["count_in_duration"] = val
        except Exception:
            changes["count_in_duration_error"] = "read-only in this Live version"
    if not changes:
        raise ValueError("No parameters specified")
    return changes


# --- Selection State ---


@command("get_selection_state")
def get_selection_state(song, ctrl=None) -> dict:
    """Get what is currently selected in Live's UI."""
    result = {}

    # Selected track
    try:
        sel_track = song.view.selected_track
        if sel_track:
            # Find track index
            for i, t in enumerate(song.tracks):
                if t == sel_track:
                    result["selected_track"] = {"index": i, "name": t.name, "type": "track"}
                    break
            else:
                for i, t in enumerate(song.return_tracks):
                    if t == sel_track:
                        result["selected_track"] = {"index": i, "name": t.name, "type": "return"}
                        break
                else:
                    if sel_track == song.master_track:
                        result["selected_track"] = {"index": 0, "name": "Master", "type": "master"}
    except Exception:
        result["selected_track"] = None

    # Selected scene
    try:
        sel_scene = song.view.selected_scene
        if sel_scene:
            for i, s in enumerate(song.scenes):
                if s == sel_scene:
                    result["selected_scene"] = {"index": i, "name": s.name}
                    break
    except Exception:
        result["selected_scene"] = None

    # Detail clip
    try:
        detail_clip = song.view.detail_clip
        if detail_clip:
            result["detail_clip"] = {
                "name": detail_clip.name,
                "is_midi": detail_clip.is_midi_clip,
                "is_audio": detail_clip.is_audio_clip,
                "length": detail_clip.length,
            }
    except Exception:
        result["detail_clip"] = None

    # Draw mode and follow song
    try:
        result["draw_mode"] = song.view.draw_mode
    except Exception:
        result["draw_mode"] = None
    try:
        result["follow_song"] = song.view.follow_song
    except Exception:
        result["follow_song"] = None

    # Highlighted clip slot
    try:
        hcs = song.view.highlighted_clip_slot
        if hcs:
            result["highlighted_clip_slot_has_clip"] = hcs.has_clip
    except Exception:
        pass

    return result


# --- Link Sync ---


@command("get_link_status")
def get_link_status(song, ctrl=None) -> dict:
    """Get Ableton Link sync status."""
    result = {
        "link_enabled": song.is_ableton_link_enabled,
    }
    try:
        result["start_stop_sync_enabled"] = song.is_ableton_link_start_stop_sync_enabled
    except Exception:
        result["start_stop_sync_enabled"] = None
    return result


@command("set_link_enabled", modifying=True)
def set_link_enabled(song, enabled: bool = None, start_stop_sync: bool = None, ctrl=None) -> dict:
    """Enable/disable Ableton Link and start/stop sync."""
    changes = {}
    if enabled is not None:
        song.is_ableton_link_enabled = bool(enabled)
        changes["link_enabled"] = bool(enabled)
    if start_stop_sync is not None:
        song.is_ableton_link_start_stop_sync_enabled = bool(start_stop_sync)
        changes["start_stop_sync_enabled"] = bool(start_stop_sync)
    if not changes:
        raise ValueError("No parameters specified")
    return changes


# --- Tuning System ---


@command("get_tuning_system")
def get_tuning_system(song, ctrl=None) -> dict:
    """Get the current tuning system settings."""
    ts = song.tuning_system
    result = {}
    try:
        result["name"] = ts.name
    except Exception:
        result["name"] = "Equal Temperament"
    try:
        result["pseudo_octave_in_cents"] = ts.pseudo_octave_in_cents
    except Exception:
        result["pseudo_octave_in_cents"] = 1200.0
    try:
        result["lowest_note"] = ts.lowest_note
    except Exception:
        result["lowest_note"] = None
    try:
        result["highest_note"] = ts.highest_note
    except Exception:
        result["highest_note"] = None
    try:
        result["reference_pitch"] = ts.reference_pitch
    except Exception:
        result["reference_pitch"] = None
    try:
        result["note_tunings"] = ts.note_tunings
    except Exception:
        result["note_tunings"] = None
    return result


# --- Application View ---


@command("get_view_state")
def get_view_state(song, ctrl=None) -> dict:
    """Get the current state of Live's application views."""
    import Live
    app = Live.Application.get_application()
    view = app.view
    views = ["Browser", "Arranger", "Session", "Detail", "Detail/Clip", "Detail/DeviceChain"]
    result = {
        "focused_view": view.focused_document_view,
        "browse_mode": view.browse_mode,
        "views": {},
    }
    for v in views:
        try:
            result["views"][v] = view.is_view_visible(v)
        except Exception:
            result["views"][v] = None
    return result


@command("set_view", modifying=True)
def set_view(song, action: str, view_name: str, ctrl=None) -> dict:
    """Show, hide, or focus a view in Live's UI.

    Args:
        action: 'show', 'hide', 'focus', or 'toggle_browse'
        view_name: 'Browser', 'Arranger', 'Session', 'Detail', 'Detail/Clip', 'Detail/DeviceChain'
    """
    import Live
    app = Live.Application.get_application()
    view = app.view

    if action == "show":
        view.show_view(view_name)
    elif action == "hide":
        view.hide_view(view_name)
    elif action == "focus":
        view.focus_view(view_name)
    elif action == "toggle_browse":
        view.toggle_browse()
    else:
        raise ValueError("action must be 'show', 'hide', 'focus', or 'toggle_browse', got '{0}'".format(action))

    return {"action": action, "view_name": view_name}


@command("zoom_scroll_view", modifying=True)
def zoom_scroll_view(song, action: str, direction: int, view_name: str, modifier_pressed: bool = False, ctrl=None) -> dict:
    """Zoom or scroll a view in Live's UI.

    Args:
        action: 'zoom' or 'scroll'
        direction: 0=up, 1=down, 2=left, 3=right
        view_name: 'Arranger', 'Session', 'Browser', 'Detail/DeviceChain'
        modifier_pressed: Modifies behavior (e.g. zoom only selected track height)
    """
    import Live
    app = Live.Application.get_application()
    view = app.view

    direction = int(direction)
    if direction < 0 or direction > 3:
        raise ValueError("direction must be 0-3, got {0}".format(direction))

    if action == "zoom":
        view.zoom_view(direction, view_name, bool(modifier_pressed))
    elif action == "scroll":
        view.scroll_view(direction, view_name, bool(modifier_pressed))
    else:
        raise ValueError("action must be 'zoom' or 'scroll', got '{0}'".format(action))

    return {"action": action, "direction": direction, "view_name": view_name}


# --- Stop All Clips ---


@command("stop_all_clips", modifying=True)
def stop_all_clips(song, ctrl=None) -> dict:
    """Stop all playing clips in the Live Set."""
    song.stop_all_clips()
    return {"stopped": True}


@command("capture_and_insert_scene", modifying=True)
def capture_and_insert_scene(song, ctrl=None) -> dict:
    """Capture currently playing clips into a new scene."""
    song.capture_and_insert_scene()
    new_scene_idx = list(song.scenes).index(song.view.selected_scene)
    return {
        "captured": True,
        "scene_index": new_scene_idx,
        "scene_name": song.scenes[new_scene_idx].name,
    }


@command("get_song_file_path")
def get_song_file_path(song, ctrl=None) -> dict:
    """Get the file path of the current Live Set."""
    return {"file_path": str(song.file_path) if song.file_path else None}


@command("set_session_record", modifying=True)
def set_session_record(song, enabled: bool, ctrl=None) -> dict:
    """Enable or disable session recording."""
    song.session_record = bool(enabled)
    return {"session_record": song.session_record}


# --- Playing Clips ---


# --- v4.0: Song-level features ---


@command("get_song_data")
def get_song_data(song, key: str, ctrl=None) -> dict:
    """Get persistent data stored in the Live Set by key."""
    val = song.get_data(str(key), None)
    return {"key": str(key), "value": val}


@command("set_song_data", modifying=True)
def set_song_data(song, key: str, value: str, ctrl=None) -> dict:
    """Store persistent data in the Live Set (survives save/load)."""
    song.set_data(str(key), value)
    return {"key": str(key), "value": value, "stored": True}


@command("end_undo_step", modifying=True)
def end_undo_step(song, ctrl=None) -> dict:
    """End the current undo step, grouping preceding operations into one undo action."""
    song.end_undo_step()
    return {"ended": True}


@command("get_song_length")
def get_song_length(song, ctrl=None) -> dict:
    """Get the total song length and last event time in beats."""
    result = {"song_length": song.song_length}
    try:
        result["last_event_time"] = song.last_event_time
    except Exception:
        pass
    result["tempo"] = song.tempo
    result["current_time"] = song.current_song_time
    return result


@command("get_beat_time")
def get_beat_time(song, ctrl=None) -> dict:
    """Get current song time as structured bars:beats:sub_division:ticks."""
    bt = song.get_current_beats_song_time()
    result = {
        "bars": bt.bars,
        "beats": bt.beats,
        "sub_division": bt.sub_division,
        "ticks": bt.ticks,
        "raw_beats": song.current_song_time,
    }
    try:
        loop_bt = song.get_beats_loop_start()
        result["loop_start"] = {"bars": loop_bt.bars, "beats": loop_bt.beats,
                                 "sub_division": loop_bt.sub_division, "ticks": loop_bt.ticks}
    except Exception:
        pass
    try:
        loop_len = song.get_beats_loop_length()
        result["loop_length"] = {"bars": loop_len.bars, "beats": loop_len.beats,
                                  "sub_division": loop_len.sub_division, "ticks": loop_len.ticks}
    except Exception:
        pass
    return result


@command("get_smpte_time")
def get_smpte_time(song, time_format: int = 0, ctrl=None) -> dict:
    """Get current song time in SMPTE format.

    Args:
        time_format: 0=ms, 1=smpte_24, 2=smpte_25, 3=smpte_29, 4=smpte_30, 5=smpte_30_drop
    """
    st = song.get_current_smpte_song_time(int(time_format))
    return {
        "hours": st.hours,
        "minutes": st.minutes,
        "seconds": st.seconds,
        "frames": st.frames,
        "format": int(time_format),
    }


@command("get_all_scales")
def get_all_scales(song, ctrl=None) -> dict:
    """Get all available scale names and intervals."""
    from Live.Song import get_all_scales_ordered
    scales = get_all_scales_ordered()
    result = []
    for scale in scales:
        if isinstance(scale, (tuple, list)) and len(scale) >= 2:
            result.append({"name": scale[0], "intervals": list(scale[1])})
        else:
            result.append(str(scale))
    return {"scales": result, "count": len(result)}


@command("nudge_tempo", modifying=True)
def nudge_tempo(song, direction: str, ctrl=None) -> dict:
    """Nudge the tempo up or down momentarily.

    Args:
        direction: "up" or "down"
    """
    if direction == "up":
        song.nudge_up = True
        song.nudge_up = False
        return {"nudged": "up", "tempo": song.tempo}
    elif direction == "down":
        song.nudge_down = True
        song.nudge_down = False
        return {"nudged": "down", "tempo": song.tempo}
    else:
        raise ValueError("direction must be 'up' or 'down'")


@command("get_appointed_device")
def get_appointed_device(song, ctrl=None) -> dict:
    """Get the currently appointed (selected) device."""
    dev = song.appointed_device
    if dev is None:
        return {"appointed_device": None}
    return {
        "name": dev.name,
        "class_name": dev.class_name,
        "is_active": dev.is_active if hasattr(dev, 'is_active') else None,
        "parameter_count": len(dev.parameters) if hasattr(dev, 'parameters') else 0,
    }


@command("get_count_in_duration")
def get_count_in_duration(song, ctrl=None) -> dict:
    """Get the count-in duration setting (0=None, 1=1 Bar, 2=2 Bars, 3=4 Bars)."""
    return {
        "count_in_duration": song.count_in_duration,
        "is_counting_in": getattr(song, "is_counting_in", False),
    }


# --- v4.0: View & UI Control ---


@command("set_draw_mode", modifying=True)
def set_draw_mode(song, enabled: bool, ctrl=None) -> dict:
    """Toggle envelope/note draw mode."""
    song.view.draw_mode = bool(enabled)
    return {"draw_mode": song.view.draw_mode}


@command("set_follow_song", modifying=True)
def set_follow_song(song, enabled: bool, ctrl=None) -> dict:
    """Toggle follow song (auto-scroll arrangement to playback position)."""
    song.view.follow_song = bool(enabled)
    return {"follow_song": song.view.follow_song}


@command("get_highlighted_clip_slot")
def get_highlighted_clip_slot(song, ctrl=None) -> dict:
    """Get the currently highlighted clip slot in Session View."""
    cs = song.view.highlighted_clip_slot
    if cs is None:
        return {"highlighted_clip_slot": None}
    result = {"has_clip": cs.has_clip}
    if cs.has_clip and cs.clip:
        result["clip_name"] = cs.clip.name
    return result


@command("select_device", modifying=True)
def select_device(song, track_index: int, device_index: int, track_type: str = "track", ctrl=None) -> dict:
    """Select a device in the detail view."""
    if track_type == "return":
        track = song.return_tracks[int(track_index)]
    elif track_type == "master":
        track = song.master_track
    else:
        track = song.tracks[int(track_index)]
    device = track.devices[int(device_index)]
    song.view.select_device(device)
    return {"selected": True, "device_name": device.name, "track_name": track.name}


@command("get_selected_parameter")
def get_selected_parameter(song, ctrl=None) -> dict:
    """Get the currently selected device parameter."""
    param = song.view.selected_parameter
    if param is None:
        return {"selected_parameter": None}
    return {
        "name": param.name,
        "value": param.value,
        "min": param.min,
        "max": param.max,
        "is_quantized": param.is_quantized,
    }


@command("select_instrument", modifying=True)
def select_instrument(song, track_index: int, ctrl=None) -> dict:
    """Select the instrument on a track (if it has one)."""
    track = song.tracks[int(track_index)]
    found = track.view.select_instrument()
    return {"selected": found, "track_name": track.name}


@command("get_playing_clips")
def get_playing_clips(song, ctrl=None) -> dict:
    """Get all currently playing/triggered clips across all tracks."""
    playing = []
    for track_idx, track in enumerate(song.tracks):
        try:
            slot_idx = track.playing_slot_index
            fired_idx = track.fired_slot_index
            if slot_idx >= 0:
                try:
                    clip = track.clip_slots[slot_idx].clip
                    playing.append({
                        "track_index": track_idx,
                        "track_name": track.name,
                        "clip_index": slot_idx,
                        "clip_name": clip.name if clip else "",
                        "status": "playing",
                    })
                except Exception:
                    playing.append({
                        "track_index": track_idx,
                        "track_name": track.name,
                        "clip_index": slot_idx,
                        "clip_name": "",
                        "status": "playing",
                    })
            if fired_idx >= 0 and fired_idx != slot_idx:
                try:
                    clip = track.clip_slots[fired_idx].clip
                    playing.append({
                        "track_index": track_idx,
                        "track_name": track.name,
                        "clip_index": fired_idx,
                        "clip_name": clip.name if clip else "",
                        "status": "triggered",
                    })
                except Exception:
                    playing.append({
                        "track_index": track_idx,
                        "track_name": track.name,
                        "clip_index": fired_idx,
                        "clip_name": "",
                        "status": "triggered",
                    })
        except Exception:
            pass
    return {"playing_clips": playing, "count": len(playing)}
