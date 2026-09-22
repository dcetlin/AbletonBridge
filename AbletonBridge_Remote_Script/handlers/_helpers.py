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


MAX_AUTOMATION_STEPS = 4000
AUTOMATION_WRITE_BUDGET_SECONDS = 12.0


def budget_automation_steps(points, resolution, max_steps=MAX_AUTOMATION_STEPS):
    """Auto-coarsen resolution if interpolated step count would exceed budget."""
    if len(points) < 2:
        return resolution, len(points)
    total_time = max(float(p.get("time", 0)) for p in points) - min(float(p.get("time", 0)) for p in points)
    if total_time <= 0 or resolution <= 0:
        return resolution, len(points)
    step_count = int(total_time / resolution)
    if step_count <= max_steps:
        return resolution, step_count
    coarsened = total_time / max_steps
    return coarsened, max_steps


def interpolate_automation(points, resolution=0.0625, mode="hold"):
    """Interpolate between automation breakpoints at the given resolution.

    Args:
        points: List of dicts. Required keys: "time", "value".
            Optional per-point keys: "interpolation" (overrides mode), "exponent" (default 3.0).
        resolution: Beats between interpolated points (default 0.0625 = 64th note).
        mode: Default interpolation: "hold", "linear", "exponential", "ease_in", "ease_out".
    """
    if mode == "hold" or len(points) < 2:
        # Check if any individual point overrides hold
        has_override = any(p.get("interpolation") and p.get("interpolation") != "hold" for p in points)
        if not has_override:
            return points

    sorted_pts = sorted(points, key=lambda p: float(p.get("time", 0.0)))
    result = []

    for i in range(len(sorted_pts) - 1):
        t0 = float(sorted_pts[i]["time"])
        v0 = float(sorted_pts[i]["value"])
        t1 = float(sorted_pts[i + 1]["time"])
        v1 = float(sorted_pts[i + 1]["value"])

        seg_mode = sorted_pts[i].get("interpolation", mode)
        seg_exp = float(sorted_pts[i].get("exponent", 3.0))

        # Exponent-driven curves are only defined for a positive exponent. A zero
        # or negative exponent is degenerate: "exponential" divides by zero, and
        # the easings hit 0**0 / 0**-1 anomalies (ease_in crashes at frac=0). Fall
        # back to linear across all three so a bad exponent can never crash.
        if seg_mode in ("exponential", "ease_in", "ease_out") and seg_exp <= 1e-9:
            seg_mode = "linear"

        dt = t1 - t0
        if dt <= 0 or seg_mode == "hold":
            result.append({"time": t0, "value": v0})
            continue

        steps = max(1, int(dt / resolution))
        for s in range(steps):
            frac = s / steps
            t = t0 + frac * dt

            if seg_mode == "linear":
                v = v0 + frac * (v1 - v0)
            elif seg_mode == "exponential":
                # seg_exp > 1e-9 here (degenerate exponents degraded to linear above).
                v = v0 + (v1 - v0) * (math.exp(frac * seg_exp) - 1) / (math.exp(seg_exp) - 1)
            elif seg_mode == "ease_in":
                v = v0 + (v1 - v0) * (frac ** seg_exp)
            elif seg_mode == "ease_out":
                v = v0 + (v1 - v0) * (1 - (1 - frac) ** seg_exp)
            else:
                v = v0 + frac * (v1 - v0)

            result.append({"time": round(t, 6), "value": round(v, 6)})

    last = sorted_pts[-1]
    result.append({"time": round(float(last["time"]), 6), "value": round(float(last["value"]), 6)})
    return result


def verify_automation(envelope, expected_points, param_min, param_max, epsilon=0.01):
    """Read back automation and compare. Returns {verdict, median_error, max_error, samples}."""
    if not expected_points:
        return {"verdict": "match", "median_error": 0, "max_error": 0, "samples": 0}
    errors = []
    for point in expected_points:
        t = float(point.get("time", 0.0))
        expected = max(param_min, min(param_max, float(point.get("value", 0.0))))
        try:
            actual = envelope.value_at_time(t)
            errors.append(abs(actual - expected))
        except Exception:
            errors.append(abs(expected))
    sorted_errors = sorted(errors)
    median_err = sorted_errors[len(sorted_errors) // 2]
    max_err = max(errors)
    if max_err < epsilon:
        verdict = "match"
    elif median_err < epsilon:
        verdict = "drift"
    else:
        verdict = "mismatch"
    return {"verdict": verdict, "median_error": round(median_err, 6), "max_error": round(max_err, 6), "samples": len(errors)}
