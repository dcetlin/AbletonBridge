"""Clip creation, notes, naming, fire/stop, delete, colors, loop, markers."""

from __future__ import absolute_import, print_function, unicode_literals

import collections.abc

from ._helpers import get_track, get_clip_slot, get_clip
from ._registry import command


@command("create_clip", modifying=True)
def create_clip(song, track_index: int, clip_index: int, length: float, ctrl=None) -> dict:
    """Create a new MIDI clip in the specified track and clip slot."""
    track, clip_slot = get_clip_slot(song, track_index, clip_index)
    if clip_slot.has_clip:
        raise ValueError("Clip slot already has a clip")
    length = float(length)
    if length <= 0:
        raise ValueError("Clip length must be positive, got {0}".format(length))
    clip_slot.create_clip(length)
    return {
        "name": clip_slot.clip.name,
        "length": clip_slot.clip.length,
    }


@command("add_notes_to_clip", modifying=True)
def add_notes_to_clip(song, track_index: int, clip_index: int, notes: list, ctrl=None) -> dict:
    """Add MIDI notes to a clip."""
    _, clip = get_clip(song, track_index, clip_index)

    # Validate and normalize note data
    note_specs = []
    for note in notes:
        note_specs.append({
            "pitch": max(0, min(127, int(note.get("pitch", 60)))),
            "start_time": max(0.0, float(note.get("start_time", 0.0))),
            "duration": max(0.01, float(note.get("duration", 0.25))),
            "velocity": max(1, min(127, int(note.get("velocity", 100)))),
            "mute": bool(note.get("mute", False)),
        })

    import Live
    specs = []
    for s in note_specs:
        specs.append(Live.Clip.MidiNoteSpecification(
            pitch=s["pitch"], start_time=s["start_time"],
            duration=s["duration"], velocity=s["velocity"],
            mute=s["mute"]))
    clip.add_new_notes(tuple(specs))
    return {"note_count": len(notes)}


@command("set_clip_name", modifying=True)
def set_clip_name(song, track_index: int, clip_index: int, name: str, ctrl=None) -> dict:
    """Set the name of a clip."""
    _, clip = get_clip(song, track_index, clip_index)
    clip.name = name
    return {"name": clip.name}


@command("fire_clip", modifying=True)
def fire_clip(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Fire a clip."""
    _, clip_slot = get_clip_slot(song, track_index, clip_index)
    if not clip_slot.has_clip:
        raise ValueError("No clip in slot")
    clip_slot.fire()
    return {"fired": True}


@command("stop_clip", modifying=True)
def stop_clip(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Stop a clip."""
    _, clip_slot = get_clip_slot(song, track_index, clip_index)
    clip_slot.stop()
    return {"stopped": True}


@command("delete_clip", modifying=True)
def delete_clip(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Delete a clip from a clip slot."""
    _, clip_slot = get_clip_slot(song, track_index, clip_index)
    if not clip_slot.has_clip:
        raise ValueError("No clip in slot")
    clip_name = clip_slot.clip.name
    clip_slot.delete_clip()
    return {
        "deleted": True,
        "clip_name": clip_name,
        "track_index": track_index,
        "clip_index": clip_index,
    }


@command("get_clip_info")
def get_clip_info(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Get detailed information about a clip."""
    _, clip = get_clip(song, track_index, clip_index)

    result = {
        "name": clip.name,
        "length": clip.length,
        "is_playing": clip.is_playing,
        "is_recording": clip.is_recording,
        "is_midi_clip": hasattr(clip, 'get_notes'),
    }

    # Try to get additional properties if available
    try:
        if hasattr(clip, 'start_marker'):
            result["start_marker"] = clip.start_marker
        if hasattr(clip, 'end_marker'):
            result["end_marker"] = clip.end_marker
        if hasattr(clip, 'loop_start'):
            result["loop_start"] = clip.loop_start
        if hasattr(clip, 'loop_end'):
            result["loop_end"] = clip.loop_end
        if hasattr(clip, 'looping'):
            result["looping"] = clip.looping
        if hasattr(clip, 'warping'):
            result["warping"] = clip.warping
        if hasattr(clip, 'color_index'):
            result["color_index"] = clip.color_index
    except Exception:
        pass

    # Playing/triggered status
    try:
        result["is_triggered"] = clip.is_triggered
    except Exception:
        pass
    try:
        result["playing_position"] = clip.playing_position
    except Exception:
        pass
    try:
        result["launch_mode"] = int(clip.launch_mode)
    except Exception:
        pass
    try:
        result["velocity_amount"] = clip.velocity_amount
    except Exception:
        pass
    try:
        result["legato"] = clip.legato
    except Exception:
        pass

    return result


@command("duplicate_clip", modifying=True)
def duplicate_clip(song, track_index: int, clip_index: int, target_clip_index: int, ctrl=None) -> dict:
    """Duplicate a clip to another slot on the same track."""
    track = get_track(song, track_index)
    if clip_index < 0 or clip_index >= len(track.clip_slots):
        raise IndexError("Source clip index out of range")
    if target_clip_index < 0 or target_clip_index >= len(track.clip_slots):
        raise IndexError("Target clip index out of range")
    source_slot = track.clip_slots[clip_index]
    target_slot = track.clip_slots[target_clip_index]
    if not source_slot.has_clip:
        raise ValueError("No clip in source slot")
    if target_slot.has_clip:
        raise ValueError("Target slot already has a clip")
    source_slot.duplicate_clip_to(target_slot)
    return {
        "duplicated": True,
        "source_index": clip_index,
        "target_index": target_clip_index,
        "clip_name": source_slot.clip.name,
    }


@command("set_clip_looping", modifying=True)
def set_clip_looping(song, track_index: int, clip_index: int, looping: bool, ctrl=None) -> dict:
    """Set the looping state of a clip."""
    _, clip = get_clip(song, track_index, clip_index)
    clip.looping = bool(int(looping))
    return {
        "track_index": track_index,
        "clip_index": clip_index,
        "looping": clip.looping,
    }


@command("set_clip_loop_points", modifying=True)
def set_clip_loop_points(song, track_index: int, clip_index: int, loop_start: float, loop_end: float, ctrl=None) -> dict:
    """Set the loop start and end points of a clip."""
    _, clip = get_clip(song, track_index, clip_index)

    loop_start = float(loop_start)
    loop_end = float(loop_end)
    if loop_start >= loop_end:
        raise ValueError(
            "loop_start ({0}) must be less than loop_end ({1})".format(loop_start, loop_end))

    # Set in safe order to avoid loop_start >= loop_end errors
    if loop_end > clip.loop_start:
        clip.loop_end = loop_end
        clip.loop_start = loop_start
    else:
        clip.loop_start = loop_start
        clip.loop_end = loop_end

    return {
        "track_index": track_index,
        "clip_index": clip_index,
        "loop_start": clip.loop_start,
        "loop_end": clip.loop_end,
    }


@command("set_clip_color", modifying=True)
def set_clip_color(song, track_index: int, clip_index: int, color_index: int, ctrl=None) -> dict:
    """Set the color of a clip."""
    _, clip = get_clip(song, track_index, clip_index)
    color_index = int(color_index)
    if color_index < 0 or color_index > 69:
        raise ValueError("color_index must be between 0 and 69, got {0}".format(color_index))
    clip.color_index = color_index
    return {
        "track_index": track_index,
        "clip_index": clip_index,
        "color_index": clip.color_index,
    }


@command("crop_clip", modifying=True)
def crop_clip(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Trim clip to its loop region."""
    _, clip = get_clip(song, track_index, clip_index)
    if not hasattr(clip, 'crop'):
        raise RuntimeError("clip.crop() not available in this Live version")
    clip.crop()
    return {
        "cropped": True,
        "new_length": clip.length,
        "clip_name": clip.name,
    }


@command("duplicate_clip_loop", modifying=True)
def duplicate_clip_loop(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Double the loop content of a clip."""
    _, clip = get_clip(song, track_index, clip_index)
    if not hasattr(clip, 'duplicate_loop'):
        raise RuntimeError("clip.duplicate_loop() not available in this Live version")
    old_length = clip.length
    clip.duplicate_loop()
    return {
        "old_length": old_length,
        "new_length": clip.length,
        "clip_name": clip.name,
    }


@command("set_clip_start_end", modifying=True)
def set_clip_start_end(song, track_index: int, clip_index: int, start_marker: float = None, end_marker: float = None, ctrl=None) -> dict:
    """Set clip start_marker and end_marker."""
    _, clip = get_clip(song, track_index, clip_index)

    if start_marker is not None and end_marker is not None:
        sm = float(start_marker)
        em = float(end_marker)
        if sm >= em:
            raise ValueError(
                "start_marker ({0}) must be less than end_marker ({1})".format(sm, em))
        # Safe order: set the "expanding" side first
        if em > clip.start_marker:
            clip.end_marker = em
            clip.start_marker = sm
        else:
            clip.start_marker = sm
            clip.end_marker = em
    elif start_marker is not None:
        sm = float(start_marker)
        if sm >= clip.end_marker:
            raise ValueError(
                "start_marker ({0}) must be less than current end_marker ({1})".format(
                    sm, clip.end_marker))
        clip.start_marker = sm
    elif end_marker is not None:
        em = float(end_marker)
        if clip.start_marker >= em:
            raise ValueError(
                "end_marker ({0}) must be greater than current start_marker ({1})".format(
                    em, clip.start_marker))
        clip.end_marker = em

    return {
        "start_marker": clip.start_marker,
        "end_marker": clip.end_marker,
        "clip_name": clip.name,
    }


@command("set_clip_pitch", modifying=True)
def set_clip_pitch(song, track_index: int, clip_index: int, pitch_coarse: int = None, pitch_fine: int = None, ctrl=None) -> dict:
    """Set pitch transposition for an audio clip.

    Args:
        pitch_coarse: Semitones (-48 to +48)
        pitch_fine: Cents (-50 to +50)
    """
    _, clip = get_clip(song, track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("Clip is not an audio clip")
    if pitch_coarse is not None:
        pitch_coarse = int(pitch_coarse)
        if pitch_coarse < -48 or pitch_coarse > 48:
            raise ValueError(
                "pitch_coarse must be between -48 and +48 semitones, got {0}".format(pitch_coarse))
        clip.pitch_coarse = pitch_coarse
    if pitch_fine is not None:
        pitch_fine = float(pitch_fine)
        if pitch_fine < -50 or pitch_fine > 50:
            raise ValueError(
                "pitch_fine must be between -50 and +50 cents, got {0}".format(pitch_fine))
        clip.pitch_fine = pitch_fine
    return {
        "pitch_coarse": clip.pitch_coarse,
        "pitch_fine": clip.pitch_fine,
        "clip_name": clip.name,
    }


@command("set_clip_launch_mode", modifying=True)
def set_clip_launch_mode(song, track_index: int, clip_index: int, launch_mode: int, ctrl=None) -> dict:
    """Set the launch mode for a clip.

    Args:
        launch_mode: 0=trigger, 1=gate, 2=toggle, 3=repeat
    """
    _, clip = get_clip(song, track_index, clip_index)
    launch_mode = int(launch_mode)
    if launch_mode < 0 or launch_mode > 3:
        raise ValueError(
            "launch_mode must be 0-3 (trigger/gate/toggle/repeat), got {0}".format(launch_mode))
    clip.launch_mode = launch_mode
    return {
        "launch_mode": clip.launch_mode,
        "clip_name": clip.name,
    }


@command("set_clip_launch_quantization", modifying=True)
def set_clip_launch_quantization(song, track_index: int, clip_index: int, quantization: int, ctrl=None) -> dict:
    """Set the launch quantization for a clip.

    Args:
        quantization: 0=none, 1=8bars, 2=4bars, 3=2bars, 4=bar, 5=half,
            6=half_triplet, 7=quarter, 8=quarter_triplet, 9=eighth,
            10=eighth_triplet, 11=sixteenth, 12=sixteenth_triplet,
            13=thirtysecond, 14=global
    """
    _, clip = get_clip(song, track_index, clip_index)
    quantization = int(quantization)
    if quantization < 0 or quantization > 14:
        raise ValueError("Launch quantization must be 0-14")
    clip.launch_quantization = quantization
    return {
        "launch_quantization": clip.launch_quantization,
        "clip_name": clip.name,
    }


@command("set_clip_legato", modifying=True)
def set_clip_legato(song, track_index: int, clip_index: int, legato: bool, ctrl=None) -> dict:
    """Set the legato mode for a clip.

    Args:
        legato: True = clip plays from position of previously playing clip.
                False = clip always starts from its start position.
    """
    _, clip = get_clip(song, track_index, clip_index)
    clip.legato = bool(int(legato))
    return {
        "legato": clip.legato,
        "clip_name": clip.name,
    }


@command("audio_to_midi", modifying=True)
def audio_to_midi(song, track_index: int, clip_index: int, conversion_type: str, ctrl=None) -> dict:
    """Convert an audio clip to a MIDI clip.

    Args:
        conversion_type: 'drums', 'harmony', or 'melody'
    """
    _, clip = get_clip(song, track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("Clip is not an audio clip")
    conversion_type = str(conversion_type).lower()
    if conversion_type not in ("drums", "harmony", "melody"):
        raise ValueError("conversion_type must be 'drums', 'harmony', or 'melody'")
    try:
        from Live.Conversions import audio_to_midi_clip, AudioToMidiType
    except ImportError as imp_err:
        raise RuntimeError(
            "Audio-to-MIDI conversion requires Live 12+ "
            "(failed to import Live.Conversions: {0})".format(imp_err)
        ) from imp_err
    type_map = {
        "drums": AudioToMidiType.drums_to_midi,
        "harmony": AudioToMidiType.harmony_to_midi,
        "melody": AudioToMidiType.melody_to_midi,
    }
    audio_to_midi_clip(song, clip, type_map[conversion_type])
    return {
        "converted": True,
        "source_clip": clip.name,
        "conversion_type": conversion_type,
        "track_index": track_index,
        "clip_index": clip_index,
    }


@command("duplicate_clip_region", modifying=True)
def duplicate_clip_region(song, track_index: int, clip_index: int,
                          region_start: float, region_length: float, destination_time: float,
                          pitch: int = -1, transposition_amount: int = 0, ctrl=None) -> dict:
    """Duplicate notes in a region to another position, with optional transposition.

    MIDI clips only. If pitch is -1, all notes in the region are duplicated.

    Args:
        region_start: Start time of the region to duplicate.
        region_length: Length of the region.
        destination_time: Where to place the duplicated notes.
        pitch: Only duplicate notes at this pitch (-1 for all).
        transposition_amount: Semitones to transpose (0 for none).
    """
    _, clip = get_clip(song, track_index, clip_index)
    if clip.is_audio_clip:
        raise ValueError("duplicate_region is only available for MIDI clips")
    clip.duplicate_region(float(region_start), float(region_length),
                          float(destination_time), int(pitch), int(transposition_amount))
    return {
        "track_index": track_index,
        "clip_index": clip_index,
        "region_start": region_start,
        "region_length": region_length,
        "destination_time": destination_time,
        "pitch": pitch,
        "transposition_amount": transposition_amount,
    }


@command("move_clip_playing_pos", modifying=True)
def move_clip_playing_pos(song, track_index: int, clip_index: int, time: float, ctrl=None) -> dict:
    """Jump to a position within a currently playing clip.

    Args:
        time: The time position to jump to within the clip.
    """
    _, clip = get_clip(song, track_index, clip_index)
    clip.move_playing_pos(float(time))
    return {
        "track_index": track_index,
        "clip_index": clip_index,
        "position": float(time),
    }


@command("set_clip_grid", modifying=True)
def set_clip_grid(song, track_index: int, clip_index: int,
                   grid_quantization: float = None, grid_is_triplet: bool = None, ctrl=None) -> dict:
    """Set the MIDI editor grid resolution for a clip.

    Args:
        grid_quantization: Grid resolution value (enum int from Clip.grid_quantization).
        grid_is_triplet: True to show grid in triplet mode, False for standard.
    """
    _, clip = get_clip(song, track_index, clip_index)
    changes = {}
    if grid_quantization is not None:
        clip.view.grid_quantization = int(grid_quantization)
        changes["grid_quantization"] = int(grid_quantization)
    if grid_is_triplet is not None:
        grid_is_triplet = bool(int(grid_is_triplet))
        clip.view.grid_is_triplet = grid_is_triplet
        changes["grid_is_triplet"] = grid_is_triplet
    if not changes:
        raise ValueError("No parameters specified")
    changes["track_index"] = track_index
    changes["clip_index"] = clip_index
    return changes


# --- Follow Actions ---


@command("get_clip_follow_actions")
def get_clip_follow_actions(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Get follow action settings for a clip."""
    _, clip = get_clip(song, track_index, clip_index)
    result = {
        "track_index": track_index,
        "clip_index": clip_index,
        "clip_name": clip.name,
    }
    for prop in ("follow_action_0", "follow_action_1",
                  "follow_action_probability", "follow_action_time",
                  "follow_action_enabled", "follow_action_linked",
                  "follow_action_return_to_zero"):
        try:
            val = getattr(clip, prop)
            if hasattr(val, 'value'):
                result[prop] = int(val)
            elif isinstance(val, bool):
                result[prop] = val
            elif isinstance(val, float):
                result[prop] = val
            else:
                result[prop] = val
        except Exception:
            result[prop] = None
    return result


@command("set_clip_follow_actions", modifying=True)
def set_clip_follow_actions(song, track_index: int, clip_index: int,
                             follow_action_0: int = None, follow_action_1: int = None,
                             follow_action_probability: float = None,
                             follow_action_time: float = None,
                             follow_action_enabled: bool = None,
                             follow_action_linked: bool = None,
                             follow_action_return_to_zero: bool = None, ctrl=None) -> dict:
    """Set follow action settings for a clip.

    Args:
        follow_action_0/1: Action type enum (0=None, 1=Stop, 2=Again, 3=Prev,
            4=Next, 5=First, 6=Last, 7=Any, 8=Other, 9=Jump)
        follow_action_probability: 0.0-1.0 probability for action_0 vs action_1
        follow_action_time: Time in beats before follow action triggers
        follow_action_enabled: Enable/disable follow actions
        follow_action_linked: Link follow action time to clip end
        follow_action_return_to_zero: Return to clip start after follow action
    """
    _, clip = get_clip(song, track_index, clip_index)
    changes = {}
    if follow_action_0 is not None:
        clip.follow_action_0 = int(follow_action_0)
        changes["follow_action_0"] = int(follow_action_0)
    if follow_action_1 is not None:
        clip.follow_action_1 = int(follow_action_1)
        changes["follow_action_1"] = int(follow_action_1)
    if follow_action_probability is not None:
        val = float(follow_action_probability)
        clip.follow_action_probability = max(0.0, min(1.0, val))
        changes["follow_action_probability"] = clip.follow_action_probability
    if follow_action_time is not None:
        clip.follow_action_time = float(follow_action_time)
        changes["follow_action_time"] = float(follow_action_time)
    if follow_action_enabled is not None:
        clip.follow_action_enabled = bool(follow_action_enabled)
        changes["follow_action_enabled"] = bool(follow_action_enabled)
    if follow_action_linked is not None:
        clip.follow_action_linked = bool(follow_action_linked)
        changes["follow_action_linked"] = bool(follow_action_linked)
    if follow_action_return_to_zero is not None:
        clip.follow_action_return_to_zero = bool(follow_action_return_to_zero)
        changes["follow_action_return_to_zero"] = bool(follow_action_return_to_zero)
    if not changes:
        raise ValueError("No follow action parameters specified")
    changes["track_index"] = track_index
    changes["clip_index"] = clip_index
    changes["clip_name"] = clip.name
    return changes


# --- Extended Clip Properties ---


@command("get_clip_properties")
def get_clip_properties(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Get extended clip properties including follow actions, RAM mode, etc."""
    _, clip = get_clip(song, track_index, clip_index)
    result = {
        "track_index": track_index,
        "clip_index": clip_index,
        "name": clip.name,
        "length": clip.length,
        "is_midi_clip": hasattr(clip, 'get_notes'),
        "is_audio_clip": clip.is_audio_clip,
        "is_playing": clip.is_playing,
        "is_recording": clip.is_recording,
    }
    for prop in ("start_marker", "end_marker", "loop_start", "loop_end",
                  "looping", "warping", "color_index", "is_triggered",
                  "playing_position", "launch_mode", "velocity_amount",
                  "legato", "ram_mode", "muted", "groove",
                  "signature_numerator", "signature_denominator",
                  "start_time", "end_time", "has_envelopes",
                  "pitch_coarse", "pitch_fine", "gain"):
        try:
            result[prop] = getattr(clip, prop)
        except Exception:
            pass
    for prop in ("follow_action_0", "follow_action_1",
                  "follow_action_probability", "follow_action_time",
                  "follow_action_enabled", "follow_action_linked"):
        try:
            val = getattr(clip, prop)
            result[prop] = int(val) if hasattr(val, 'value') else val
        except Exception:
            pass
    return result


@command("set_clip_properties", modifying=True)
def set_clip_properties(song, track_index: int, clip_index: int,
                         muted: bool = None, velocity_amount: float = None, groove: float = None,
                         signature_numerator: int = None, signature_denominator: int = None,
                         ram_mode: bool = None, warping: bool = None, gain: float = None, ctrl=None) -> dict:
    """Set multiple clip properties at once."""
    _, clip = get_clip(song, track_index, clip_index)
    changes = {}
    if muted is not None:
        clip.muted = bool(muted)
        changes["muted"] = clip.muted
    if velocity_amount is not None:
        clip.velocity_amount = float(velocity_amount)
        changes["velocity_amount"] = clip.velocity_amount
    if groove is not None:
        clip.groove = groove
        changes["groove"] = clip.groove
    if signature_numerator is not None:
        clip.signature_numerator = int(signature_numerator)
        changes["signature_numerator"] = clip.signature_numerator
    if signature_denominator is not None:
        clip.signature_denominator = int(signature_denominator)
        changes["signature_denominator"] = clip.signature_denominator
    if ram_mode is not None:
        clip.ram_mode = bool(ram_mode)
        changes["ram_mode"] = clip.ram_mode
    if warping is not None:
        clip.warping = bool(warping)
        changes["warping"] = clip.warping
    if gain is not None:
        clip.gain = float(gain)
        changes["gain"] = clip.gain
    if not changes:
        raise ValueError("No clip properties specified")
    changes["track_index"] = track_index
    changes["clip_index"] = clip_index
    changes["clip_name"] = clip.name
    return changes


@command("select_all_notes", modifying=True)
def select_all_notes(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Select all notes in a MIDI clip."""
    _, clip = get_clip(song, track_index, clip_index)
    if clip.is_audio_clip:
        raise ValueError("select_all_notes is only for MIDI clips")
    clip.select_all_notes()
    return {"selected": True, "clip_name": clip.name}


@command("set_clip_start_time", modifying=True)
def set_clip_start_time(song, track_index: int, clip_index: int, time: float, ctrl=None) -> dict:
    """Set the start_time of a clip (arrangement position, Live 12.2+)."""
    _, clip = get_clip(song, track_index, clip_index)
    clip.start_time = float(time)
    return {
        "track_index": track_index,
        "clip_index": clip_index,
        "start_time": clip.start_time,
    }


@command("stop_track_clips", modifying=True)
def stop_track_clips(song, track_index: int, ctrl=None) -> dict:
    """Stop all clips on a specific track."""
    track = get_track(song, track_index)
    track.stop_all_clips()
    return {"stopped": True, "track_index": track_index, "track_name": track.name}


@command("create_arrangement_midi_clip", modifying=True)
def create_arrangement_midi_clip(song, track_index: int, time: float, length: float, ctrl=None) -> dict:
    """Create a MIDI clip in the arrangement view (Live 12.1+)."""
    track = get_track(song, track_index)
    if not track.has_midi_input:
        raise ValueError("Track {0} is not a MIDI track".format(track_index))
    if not hasattr(track, 'create_midi_clip'):
        raise RuntimeError("create_midi_clip requires Live 12.1+")
    clip = track.create_midi_clip(float(time), float(length))
    return {
        "created": True,
        "track_index": track_index,
        "clip_name": clip.name if clip else "New MIDI Clip",
        "time": float(time),
        "length": float(length),
    }


@command("create_arrangement_audio_clip", modifying=True)
def create_arrangement_audio_clip(song, track_index: int, time: float, length: float, ctrl=None) -> dict:
    """Create an audio clip in the arrangement view (Live 12.2+)."""
    track = get_track(song, track_index)
    if not track.has_audio_input:
        raise ValueError("Track {0} is not an audio track".format(track_index))
    if not hasattr(track, 'create_audio_clip'):
        raise RuntimeError("create_audio_clip requires Live 12.2+")
    clip = track.create_audio_clip(float(time), float(length))
    return {
        "created": True,
        "track_index": track_index,
        "clip_name": clip.name if clip else "New Audio Clip",
        "time": float(time),
        "length": float(length),
    }


# --- Warp Markers ---


@command("get_warp_markers")
def get_warp_markers(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Get the warp markers of an audio clip."""
    _, clip = get_clip(song, track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("Warp markers are only available on audio clips")
    markers = []
    try:
        wm = clip.warp_markers
        if isinstance(wm, dict):
            # LOM returns dict format
            wm_list = wm.get("warp_markers", [])
            for i, m in enumerate(wm_list):
                if isinstance(m, dict):
                    markers.append({
                        "index": i,
                        "beat_time": m.get("beat_time", 0.0),
                        "sample_time": m.get("sample_time", 0.0),
                    })
                else:
                    markers.append({
                        "index": i,
                        "beat_time": getattr(m, "beat_time", 0.0),
                        "sample_time": getattr(m, "sample_time", 0.0),
                    })
        elif isinstance(wm, collections.abc.Iterable) and not isinstance(wm, (str, bytes)):
            for i, m in enumerate(wm):
                markers.append({
                    "index": i,
                    "beat_time": getattr(m, "beat_time", 0.0),
                    "sample_time": getattr(m, "sample_time", 0.0),
                })
        else:
            if ctrl:
                ctrl.log_message(
                    "Unexpected warp_markers type: {0}".format(type(wm).__name__))
    except Exception as e:
        if ctrl:
            ctrl.log_message("Error reading warp markers: " + str(e))
    return {
        "track_index": track_index,
        "clip_index": clip_index,
        "warping": clip.warping,
        "warp_markers": markers,
        "count": len(markers),
    }


@command("add_warp_marker", modifying=True)
def add_warp_marker(song, track_index: int, clip_index: int, beat_time: float, sample_time: float = None, ctrl=None) -> dict:
    """Add a warp marker to an audio clip.

    Args:
        beat_time: The beat position for the warp marker.
        sample_time: The sample position (if None, auto-calculated by Live).
    """
    _, clip = get_clip(song, track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("Warp markers are only available on audio clips")
    bt = float(beat_time)
    if sample_time is not None:
        clip.add_warp_marker(bt, float(sample_time))
    else:
        clip.add_warp_marker(bt)
    return {
        "added": True,
        "beat_time": bt,
        "sample_time": float(sample_time) if sample_time is not None else None,
    }


@command("move_warp_marker", modifying=True)
def move_warp_marker(song, track_index: int, clip_index: int, beat_time: float, beat_time_distance: float, ctrl=None) -> dict:
    """Move a warp marker by a beat-time distance.

    Args:
        beat_time: Beat position of the warp marker to move.
        beat_time_distance: Amount (in beats) to shift the marker.
    """
    _, clip = get_clip(song, track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("Warp markers are only available on audio clips")
    clip.move_warp_marker(float(beat_time), float(beat_time_distance))
    return {
        "moved": True,
        "beat_time": float(beat_time),
        "beat_time_distance": float(beat_time_distance),
    }


@command("remove_warp_marker", modifying=True)
def remove_warp_marker(song, track_index: int, clip_index: int, beat_time: float, ctrl=None) -> dict:
    """Remove a warp marker from an audio clip.

    Args:
        beat_time: Beat position of the warp marker to remove.
    """
    _, clip = get_clip(song, track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("Warp markers are only available on audio clips")
    clip.remove_warp_marker(float(beat_time))
    return {
        "removed": True,
        "beat_time": float(beat_time),
    }


# --- v4.0: Additional clip operations ---


@command("deselect_all_notes", modifying=True)
def deselect_all_notes(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Deselect all notes in a MIDI clip."""
    _, clip = get_clip(song, track_index, clip_index)
    if clip.is_audio_clip:
        raise ValueError("deselect_all_notes is only for MIDI clips")
    clip.deselect_all_notes()
    return {"deselected": True, "clip_name": clip.name}


@command("get_selected_notes")
def get_selected_notes(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Get the currently selected notes in a MIDI clip."""
    _, clip = get_clip(song, track_index, clip_index)
    if clip.is_audio_clip:
        raise ValueError("get_selected_notes is only for MIDI clips")

    notes = []
    if hasattr(clip, 'get_selected_notes_extended'):
        raw = clip.get_selected_notes_extended()
        for note in raw:
            notes.append({
                "pitch": note.pitch,
                "start_time": note.start_time,
                "duration": note.duration,
                "velocity": note.velocity,
                "mute": note.mute,
                "note_id": getattr(note, "note_id", None),
                "probability": getattr(note, "probability", None),
                "velocity_deviation": getattr(note, "velocity_deviation", None),
                "release_velocity": getattr(note, "release_velocity", None),
            })
    elif hasattr(clip, 'get_selected_notes'):
        raw = clip.get_selected_notes()
        for note in raw:
            if isinstance(note, (tuple, list)):
                notes.append({
                    "pitch": note[0],
                    "start_time": note[1],
                    "duration": note[2],
                    "velocity": note[3],
                    "mute": note[4] if len(note) > 4 else False,
                })
    else:
        raise RuntimeError("Clip does not support get_selected_notes")

    return {
        "track_index": track_index,
        "clip_index": clip_index,
        "clip_name": clip.name,
        "selected_count": len(notes),
        "notes": notes,
    }


@command("set_fire_button_state", modifying=True)
def set_fire_button_state(song, track_index: int, clip_index: int, state: bool, ctrl=None) -> dict:
    """Set the clip's fire button state directly (supports all launch modes)."""
    _, clip = get_clip(song, track_index, clip_index)
    clip.set_fire_button_state(bool(state))
    return {"track_index": track_index, "clip_index": clip_index, "fire_button_state": bool(state)}


@command("clip_scrub_native", modifying=True)
def clip_scrub_native(song, track_index: int, clip_index: int, position: float, ctrl=None) -> dict:
    """Start scrubbing inside a clip (via Remote Script, not M4L)."""
    _, clip = get_clip(song, track_index, clip_index)
    clip.scrub(float(position))
    return {"scrubbing": True, "position": float(position)}


@command("clip_stop_scrub", modifying=True)
def clip_stop_scrub(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Stop scrubbing a clip."""
    _, clip = get_clip(song, track_index, clip_index)
    clip.stop_scrub()
    return {"stopped_scrub": True}


@command("clip_beat_to_sample_time")
def clip_beat_to_sample_time(song, track_index: int, clip_index: int, beat_time: float, ctrl=None) -> dict:
    """Convert beat time to sample time (audio clips only)."""
    _, clip = get_clip(song, track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("beat_to_sample_time is only for audio clips")
    sample_time = clip.beat_to_sample_time(float(beat_time))
    return {"beat_time": float(beat_time), "sample_time": sample_time}


@command("clip_sample_to_beat_time")
def clip_sample_to_beat_time(song, track_index: int, clip_index: int, sample_time: float, ctrl=None) -> dict:
    """Convert sample time to beat time (audio clips only)."""
    _, clip = get_clip(song, track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("sample_to_beat_time is only for audio clips")
    beat_time = clip.sample_to_beat_time(float(sample_time))
    return {"sample_time": float(sample_time), "beat_time": beat_time}


@command("duplicate_clip_slot", modifying=True)
def duplicate_clip_slot(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Duplicate a clip slot within a track (puts copy in next free slot)."""
    track = get_track(song, track_index)
    dest_index = track.duplicate_clip_slot(int(clip_index))
    return {
        "track_index": track_index,
        "source_clip_index": clip_index,
        "destination_clip_index": dest_index,
    }


# --- v4.0: Clip slot properties ---


@command("get_clip_slot_properties")
def get_clip_slot_properties(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Get clip slot properties (has_stop_button, is_group_slot, color)."""
    track, clip_slot = get_clip_slot(song, track_index, clip_index)
    result = {
        "track_index": track_index,
        "clip_index": clip_index,
        "has_clip": clip_slot.has_clip,
    }
    try:
        result["has_stop_button"] = clip_slot.has_stop_button
    except Exception:
        result["has_stop_button"] = None
    try:
        result["is_group_slot"] = clip_slot.is_group_slot
    except Exception:
        result["is_group_slot"] = None
    try:
        result["color_index"] = clip_slot.color_index
    except Exception:
        result["color_index"] = None
    try:
        result["color"] = clip_slot.color
    except Exception:
        result["color"] = None
    try:
        result["is_triggered"] = clip_slot.is_triggered
    except Exception:
        result["is_triggered"] = None
    try:
        result["is_playing"] = clip_slot.is_playing
    except Exception:
        result["is_playing"] = None
    try:
        result["is_recording"] = clip_slot.is_recording
    except Exception:
        result["is_recording"] = None
    return result


@command("set_clip_slot_properties", modifying=True)
def set_clip_slot_properties(song, track_index: int, clip_index: int, has_stop_button: bool = None,
                               color_index: int = None, ctrl=None) -> dict:
    """Set clip slot properties (has_stop_button, color)."""
    track, clip_slot = get_clip_slot(song, track_index, clip_index)
    changes = {}
    if has_stop_button is not None:
        clip_slot.has_stop_button = bool(has_stop_button)
        changes["has_stop_button"] = clip_slot.has_stop_button
    if color_index is not None:
        clip_slot.color_index = int(color_index)
        changes["color_index"] = clip_slot.color_index
    if not changes:
        raise ValueError("No properties specified")
    changes["track_index"] = track_index
    changes["clip_index"] = clip_index
    return changes
