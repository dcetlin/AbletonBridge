"""Shared validation helpers used by all handler modules."""

from __future__ import absolute_import, print_function, unicode_literals


def get_track(song, track_index, track_type="track"):
    """Get track by index with bounds validation.

    Args:
        song: Live song object.
        track_index: Zero-based index.
        track_type: "track" | "return" | "master".

    Returns:
        The track object.

    Raises:
        IndexError: If track_index is out of range.
    """
    if track_type == "return":
        tracks = song.return_tracks
        label = "Return track"
    elif track_type == "master":
        return song.master_track
    else:
        tracks = song.tracks
        label = "Track"
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError("{0} index out of range".format(label))
    return tracks[track_index]


def get_clip_slot(song, track_index, clip_index, track_type="track"):
    """Get a clip slot with full track + slot bounds validation.

    Returns:
        (track, clip_slot) tuple.

    Raises:
        IndexError: If track or clip index is out of range.
    """
    track = get_track(song, track_index, track_type)
    if clip_index < 0 or clip_index >= len(track.clip_slots):
        raise IndexError("Clip index out of range")
    return track, track.clip_slots[clip_index]


def get_clip(song, track_index, clip_index, track_type="track"):
    """Get a clip with full validation chain (track + slot + has_clip).

    Returns:
        (track, clip) tuple.

    Raises:
        IndexError: If track or clip index is out of range.
        Exception: If the slot has no clip.
    """
    track, slot = get_clip_slot(song, track_index, clip_index, track_type)
    if not slot.has_clip:
        raise ValueError("No clip in slot (track={0}, clip={1})".format(track_index, clip_index))
    return track, slot.clip


def get_scene(song, scene_index):
    """Get a scene by index with bounds validation.

    Returns:
        The scene object.

    Raises:
        IndexError: If scene_index is out of range.
    """
    if scene_index < 0 or scene_index >= len(song.scenes):
        raise IndexError("Scene index out of range")
    return song.scenes[scene_index]


def safe_getattr(obj, attr, default=None):
    """Get an attribute, returning default if access raises any exception."""
    try:
        return getattr(obj, attr)
    except Exception:
        return default


import math


def interpolate_automation(points, resolution=0.0625, mode="hold"):
    """Interpolate between automation breakpoints at the given resolution.

    Args:
        points: List of {"time": float, "value": float} dicts, sorted by time.
        resolution: Beats between interpolated points (default 0.0625 = 64th note).
        mode: "hold" (staircase, no interpolation), "linear", "exponential".

    Returns:
        List of {"time": float, "value": float} dicts — the dense output points.
    """
    if mode == "hold" or len(points) < 2:
        return points

    sorted_pts = sorted(points, key=lambda p: float(p.get("time", 0.0)))
    result = []

    for i in range(len(sorted_pts) - 1):
        t0 = float(sorted_pts[i]["time"])
        v0 = float(sorted_pts[i]["value"])
        t1 = float(sorted_pts[i + 1]["time"])
        v1 = float(sorted_pts[i + 1]["value"])

        dt = t1 - t0
        if dt <= 0:
            result.append({"time": t0, "value": v0})
            continue

        steps = max(1, int(dt / resolution))
        for s in range(steps):
            frac = s / steps
            t = t0 + frac * dt

            if mode == "linear":
                v = v0 + frac * (v1 - v0)
            elif mode == "exponential":
                v = v0 + (v1 - v0) * (math.exp(frac * 3) - 1) / (math.exp(3) - 1)
            else:
                v = v0

            result.append({"time": round(t, 6), "value": round(v, 6)})

    # Add the final point
    last = sorted_pts[-1]
    result.append({"time": round(float(last["time"]), 6), "value": round(float(last["value"]), 6)})
    return result
