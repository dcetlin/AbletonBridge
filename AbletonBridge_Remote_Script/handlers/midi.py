"""MIDI: get/set notes, quantize, transpose, clear, capture, groove."""

from __future__ import absolute_import, print_function, unicode_literals

from ._helpers import get_clip
from ._registry import command


@command("get_clip_notes")
def get_clip_notes(song, track_index: int, clip_index: int, start_time: float, time_span: float, start_pitch: int, pitch_span: int, ctrl=None) -> dict:
    """Get MIDI notes from a clip."""
    clip = _get_midi_clip(song, track_index, clip_index)

    # If time_span is 0, use entire clip length (+1 to include boundary notes)
    if time_span == 0.0:
        time_span = clip.length + 1

    # API: get_notes(start_time, start_pitch, time_span, pitch_span)
    notes_tuple = clip.get_notes(start_time, start_pitch, time_span, pitch_span)

    notes = []
    for note in notes_tuple:
        notes.append({
            "pitch": note[0],
            "start_time": note[1],
            "duration": note[2],
            "velocity": note[3],
            "mute": note[4] if len(note) > 4 else False,
        })

    return {
        "clip_name": clip.name,
        "clip_length": clip.length,
        "note_count": len(notes),
        "notes": notes,
    }


@command("add_notes_extended", modifying=True, idempotent=False)
def add_notes_extended(song, track_index: int, clip_index: int, notes: list, ctrl=None) -> dict:
    """Add MIDI notes using MidiNoteSpecification (Live 12+)."""
    import Live

    clip = _get_midi_clip(song, track_index, clip_index)

    specs = []
    for n in notes:
        kwargs = {
            "pitch": max(0, min(127, int(n.get("pitch", 60)))),
            "start_time": max(0.0, float(n.get("start_time", 0.0))),
            "duration": max(0.01, float(n.get("duration", 0.25))),
            "velocity": max(1, min(127, int(n.get("velocity", 100)))),
            "mute": bool(n.get("mute", False)),
        }
        if "probability" in n:
            kwargs["probability"] = max(0.0, min(1.0, float(n["probability"])))
        if "velocity_deviation" in n:
            kwargs["velocity_deviation"] = max(-127.0, min(127.0, float(n["velocity_deviation"])))
        if "release_velocity" in n:
            kwargs["release_velocity"] = max(0, min(127, int(n["release_velocity"])))
        specs.append(Live.Clip.MidiNoteSpecification(**kwargs))

    clip.add_new_notes(tuple(specs))
    return {"note_count": len(specs), "extended": True}


@command("get_notes_extended")
def get_notes_extended(song, track_index: int, clip_index: int, start_time: float, time_span: float, ctrl=None) -> dict:
    """Get MIDI notes with extended properties (Live 12+)."""
    clip = _get_midi_clip(song, track_index, clip_index)
    actual_time_span = time_span if time_span > 0 else clip.length + 1

    raw_notes = clip.get_notes_extended(0, 128, start_time, actual_time_span)
    notes = []
    for note in raw_notes:
        note_dict = {
            "pitch": note.pitch,
            "start_time": note.start_time,
            "duration": note.duration,
            "velocity": note.velocity,
            "mute": note.mute,
        }
        if hasattr(note, 'probability'):
            note_dict["probability"] = note.probability
        if hasattr(note, 'velocity_deviation'):
            note_dict["velocity_deviation"] = note.velocity_deviation
        if hasattr(note, 'release_velocity'):
            note_dict["release_velocity"] = note.release_velocity
        notes.append(note_dict)
    return {
        "clip_name": clip.name,
        "clip_length": clip.length,
        "note_count": len(notes),
        "extended": True,
        "notes": notes,
    }


@command("remove_notes_range", modifying=True)
def remove_notes_range(song, track_index: int, clip_index: int, from_time: float, time_span: float, from_pitch: int, pitch_span: int, ctrl=None) -> dict:
    """Remove notes within a specific time and pitch range."""
    clip = _get_midi_clip(song, track_index, clip_index)

    # Count notes before removal (+1 to include boundary notes)
    actual_time_span = time_span if time_span > 0 else clip.length + 1
    before = clip.get_notes(from_time, from_pitch, actual_time_span, pitch_span)
    count_before = len(before)

    clip.remove_notes_extended(from_pitch, pitch_span, from_time, actual_time_span)

    return {
        "removed": True,
        "notes_removed": count_before,
        "from_time": from_time,
        "time_span": actual_time_span,
        "from_pitch": from_pitch,
        "pitch_span": pitch_span,
    }


@command("clear_clip_notes", modifying=True)
def clear_clip_notes(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Remove all MIDI notes from a clip."""
    clip = _get_midi_clip(song, track_index, clip_index)

    # Count notes before removing (use clip.length + 1 to match removal range)
    notes_before = clip.get_notes(0, 0, clip.length + 1, 128)
    notes_count = len(notes_before)

    clip.remove_notes_extended(0, 128, 0, clip.length + 1)

    return {
        "cleared": True,
        "notes_removed": notes_count,
        "clip_name": clip.name,
    }


@command("quantize_clip_notes", modifying=True)
def quantize_clip_notes(song, track_index: int, clip_index: int, grid_size: float, ctrl=None) -> dict:
    """Quantize MIDI notes in a clip to a grid."""
    if grid_size <= 0:
        raise ValueError("grid_size must be greater than 0")

    clip = _get_midi_clip(song, track_index, clip_index)

    notes_tuple = clip.get_notes(0, 0, clip.length + 1, 128)
    notes_count = len(notes_tuple)

    if notes_count == 0:
        return {"quantized": True, "notes_quantized": 0, "grid_size": grid_size}

    # Map grid_size (in beats) to Live's RecordQuantization enum
    grid_map = {
        1.0: 1,     # quarter notes
        0.5: 2,     # eighth notes
        0.25: 5,    # sixteenth notes
        0.125: 8,   # thirty-second notes
    }

    if grid_size in grid_map:
        clip.quantize(grid_map[grid_size], 1.0)
    else:
        raw_notes = clip.get_notes_extended(0, 128, 0, clip.length + 1)
        for note in raw_notes:
            note.start_time = round(note.start_time / grid_size) * grid_size
        clip.apply_note_modifications(raw_notes)

    return {
        "quantized": True,
        "notes_quantized": notes_count,
        "grid_size": grid_size,
    }


@command("transpose_clip_notes", modifying=True)
def transpose_clip_notes(song, track_index: int, clip_index: int, semitones: int, ctrl=None) -> dict:
    """Transpose MIDI notes in a clip by a number of semitones."""
    clip = _get_midi_clip(song, track_index, clip_index)

    notes_tuple = clip.get_notes(0, 0, clip.length + 1, 128)
    if len(notes_tuple) == 0:
        return {"transposed": True, "notes_transposed": 0, "semitones": semitones}

    raw_notes = clip.get_notes_extended(0, 128, 0, clip.length + 1)
    for note in raw_notes:
        note.pitch = max(0, min(127, note.pitch + semitones))
    clip.apply_note_modifications(raw_notes)

    return {
        "transposed": True,
        "notes_transposed": len(notes_tuple),
        "semitones": semitones,
    }


# --- New commands from MacWhite ---


@command("capture_midi", modifying=True)
def capture_midi(song, ctrl=None) -> dict:
    """Capture recently played MIDI."""
    song.capture_midi()
    return {"captured": True}


@command("apply_groove", modifying=True)
def apply_groove(song, track_index: int, clip_index: int, groove_amount: float, ctrl=None) -> dict:
    """Set global song.groove_amount. Validates clip exists but does NOT apply per-clip groove.

    NOTE: song.groove_amount is a global setting — it affects all clips that
    have a groove assigned, not just the specified clip.  The track_index and
    clip_index parameters are used only for input validation.
    """
    _get_midi_clip(song, track_index, clip_index)  # validate clip exists
    groove_amount = float(groove_amount)
    if groove_amount < 0.0 or groove_amount > 1.0:
        raise ValueError("groove_amount must be 0.0-1.0, got {0}".format(groove_amount))
    song.groove_amount = groove_amount
    return {
        "applied_scope": "song",
        "track_index": track_index,
        "clip_index": clip_index,
        "groove_amount": song.groove_amount,
        "note": "groove_amount is a global song property — affects all clips with a groove assigned",
    }


# --- Helper ---


def _get_midi_clip(song, track_index, clip_index):
    """Get a MIDI clip with validation."""
    _, clip = get_clip(song, track_index, clip_index)
    if not hasattr(clip, 'get_notes'):
        raise TypeError("Clip is not a MIDI clip")
    return clip
