"""Automation: clip automation, track-level automation, arrangement time editing."""

from __future__ import absolute_import, print_function, unicode_literals

import re
import time as _time
from ._helpers import (
    get_track, get_clip, interpolate_automation,
    budget_automation_steps, AUTOMATION_WRITE_BUDGET_SECONDS,
    verify_automation,
)
from ._registry import command

_RE_SEND_NAME = re.compile(r'^send\s*([a-z])$')


def _find_parameter(song, track_index, parameter_name, device_index=None):
    """Find a track mixer or device parameter by name.

    When device_index is provided, only search that device's parameters
    (including rack macros named "Macro 1" through "Macro 16").
    """
    track = get_track(song, track_index)
    lower = parameter_name.lower()

    if device_index is None:
        # Check mixer parameters
        if lower == "volume":
            return track.mixer_device.volume
        elif lower in ("pan", "panning"):
            return track.mixer_device.panning

        # Check send parameters — accept "send a", "send_a", "senda", etc.
        m = _RE_SEND_NAME.match(lower.replace("_", ""))
        if m:
            send_index = ord(m.group(1).upper()) - ord("A")
            if 0 <= send_index < len(track.mixer_device.sends):
                return track.mixer_device.sends[send_index]

        # Check all device parameters
        for device in track.devices:
            for p in device.parameters:
                if p.name.lower() == lower:
                    return p
    else:
        devices = list(track.devices)
        if device_index < 0 or device_index >= len(devices):
            raise ValueError("device_index {0} out of range (track has {1} devices)".format(
                device_index, len(devices)))
        device = devices[device_index]
        for p in device.parameters:
            if p.name.lower() == lower:
                return p

    raise ValueError("Parameter '{0}' not found".format(parameter_name))


@command("create_clip_automation", modifying=True)
def create_clip_automation(song, track_index: int, clip_index: int, parameter_name: str, automation_points: list,
                           device_index: int | None = None, append: bool = False,
                           interpolation: str = "hold", resolution: float = 0.0625,
                           verify: bool = False, ctrl=None) -> dict:
    """Create automation for a parameter within a clip."""
    track, clip = get_clip(song, track_index, clip_index)

    param = _find_parameter(song, track_index, parameter_name, device_index=device_index)

    if not hasattr(clip, 'automation_envelope'):
        if hasattr(clip, 'create_automation_envelope'):
            envelope = clip.create_automation_envelope(param)
        else:
            raise RuntimeError("Clip does not support automation envelopes")
    else:
        envelope = clip.automation_envelope(param)

    if envelope is None:
        if hasattr(clip, 'create_automation_envelope'):
            envelope = clip.create_automation_envelope(param)
        if envelope is None:
            raise RuntimeError("Could not get automation envelope for parameter '{0}'".format(parameter_name))

    if not append and hasattr(envelope, 'clear'):
        try:
            envelope.clear()
        except Exception:
            pass

    resolution, planned_steps = budget_automation_steps(automation_points, resolution)

    # Always route through interpolate_automation: it self-guards (returns points
    # unchanged for pure-hold with no per-point overrides), so per-point
    # "interpolation" overrides are honored even when the curve-global mode is "hold".
    automation_points = interpolate_automation(automation_points, resolution, interpolation)

    clip_length = clip.length
    deadline = _time.time() + AUTOMATION_WRITE_BUDGET_SECONDS
    written = 0
    last_written_time = None
    for point in automation_points:
        if _time.time() > deadline:
            break
        time_val = float(point.get("time", 0.0))
        time_val = max(0.0, min(clip_length - 0.001, time_val))
        value = float(point.get("value", 0.0))
        clamped = max(param.min, min(param.max, value))
        # Duration must be > 0 or Ableton's LOM silently discards the step.
        envelope.insert_step(time_val, 0.001, clamped)
        written += 1
        last_written_time = time_val

    result = {
        "parameter": parameter_name,
        "track_index": track_index,
        "clip_index": clip_index,
        "points_added": written,
        "points_planned": len(automation_points),
        "partial": written < len(automation_points),
        "resolution_used": resolution,
        # On a partial write, the covered range is [start, last_written_time];
        # points are time-sorted, so a caller can resume past this boundary.
        "last_written_time": last_written_time,
    }
    if verify:
        result["verified"] = verify_automation(envelope, automation_points, param.min, param.max)
    return result


@command("get_clip_automation")
def get_clip_automation(song, track_index: int, clip_index: int, parameter_name: str, device_index: int | None = None, ctrl=None) -> dict:
    """Read automation envelope from a clip."""
    track, clip = get_clip(song, track_index, clip_index)

    param = _find_parameter(song, track_index, parameter_name, device_index=device_index)

    if not hasattr(clip, 'automation_envelope'):
        return {"has_automation": False, "parameter": parameter_name, "reason": "Clip does not support automation envelopes"}

    envelope = clip.automation_envelope(param)
    if envelope is None:
        return {"has_automation": False, "parameter": parameter_name}

    # Sample the envelope at evenly-spaced points
    num_samples = 64
    clip_len = clip.length
    if clip_len <= 0:
        return {"has_automation": False, "parameter": parameter_name, "reason": "Clip has zero length"}

    points = []
    step = clip_len / num_samples
    for i in range(num_samples):
        t = i * step
        try:
            val = envelope.value_at_time(t)
            points.append({"time": round(t, 4), "value": round(val, 4)})
        except Exception as e:
            if ctrl:
                ctrl.log_message("Automation sample at t={0} failed: {1}".format(round(t, 4), e))

    return {
        "has_automation": True,
        "parameter": parameter_name,
        "param_min": param.min,
        "param_max": param.max,
        "clip_length": clip_len,
        "point_count": len(points),
        "points": points,
    }


@command("clear_clip_automation", modifying=True, destructive=True)
def clear_clip_automation(song, track_index: int, clip_index: int, parameter_name: str, device_index: int | None = None, ctrl=None) -> dict:
    """Clear automation for a specific parameter in a clip."""
    track, clip = get_clip(song, track_index, clip_index)

    param = _find_parameter(song, track_index, parameter_name, device_index=device_index)

    if not hasattr(clip, 'automation_envelope'):
        raise RuntimeError("Clip does not support automation envelopes")

    envelope = clip.automation_envelope(param)
    if envelope is None:
        return {"cleared": False, "parameter": parameter_name, "reason": "No automation envelope found"}

    if hasattr(envelope, 'clear'):
        envelope.clear()
        return {"cleared": True, "parameter": parameter_name}
    else:
        raise NotImplementedError("Envelope does not support clear()")


@command("list_clip_automated_params")
def list_clip_automated_params(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """List all parameters that have automation in a clip."""
    track, clip = get_clip(song, track_index, clip_index)

    if not hasattr(clip, 'automation_envelope'):
        return {"automated_parameters": [], "count": 0, "reason": "Clip does not support automation envelopes"}

    automated = []

    # Check mixer parameters
    for name, param in [("Volume", track.mixer_device.volume), ("Pan", track.mixer_device.panning)]:
        try:
            env = clip.automation_envelope(param)
            if env is not None:
                automated.append({"name": name, "source": "Mixer"})
        except Exception:
            pass

    # Check send parameters
    for i, send in enumerate(track.mixer_device.sends):
        try:
            env = clip.automation_envelope(send)
            if env is not None:
                automated.append({"name": "Send " + chr(65 + i), "source": "Mixer"})
        except Exception:
            pass

    # Check device parameters
    for dev_idx, device in enumerate(track.devices):
        for param in device.parameters:
            try:
                env = clip.automation_envelope(param)
                if env is not None:
                    automated.append({
                        "name": param.name,
                        "source": device.name,
                        "device_index": dev_idx,
                    })
            except Exception:
                pass

    return {"automated_parameters": automated, "count": len(automated)}


# --- New: Track-level automation and arrangement time editing (from MacWhite) ---


@command("create_track_automation", modifying=True)
def create_track_automation(song, track_index: int, parameter_name: str, automation_points: list,
                            device_index: int | None = None, append: bool = False,
                            interpolation: str = "hold", resolution: float = 0.0625,
                            verify: bool = False, ctrl=None) -> dict:
    """Create automation for a track parameter (arrangement-level).

    Uses arrangement clips to access the automation envelope for the given
    parameter.  If no arrangement clip exists, attempts to create one covering
    the automation range.
    """
    track = get_track(song, track_index)
    parameter = _find_parameter(song, track_index, parameter_name, device_index=device_index)

    if not hasattr(track, "arrangement_clips"):
        raise RuntimeError(
            "Arrangement automation requires Live 11+ (track.arrangement_clips not available)"
        )

    times = [float(p.get("time", 0.0)) for p in automation_points]
    if not times:
        return {
            "parameter": parameter_name,
            "track_index": track_index,
            "points_added": 0,
            "points_planned": 0,
            "partial": False,
            "resolution_used": resolution,
            "last_written_time": None,
        }
    t_min = min(times)
    t_max = max(times)

    arr_clips = list(track.arrangement_clips)
    if not arr_clips:
        # Auto-create an arrangement clip covering the automation range
        if hasattr(track, "create_arrangement_clip"):
            end_time = t_max + 1.0
            try:
                track.create_arrangement_clip(0.0, end_time)
                arr_clips = list(track.arrangement_clips)
            except Exception as create_err:
                raise ValueError(
                    "No arrangement clips on track {0} and auto-create failed: {1}. "
                    "Create a clip manually first.".format(track_index, create_err)
                )
        else:
            raise ValueError(
                "No arrangement clips on track {0} and create_arrangement_clip is not "
                "available (requires Live 12+). Create a clip manually first.".format(track_index)
            )

    # Pick the first arrangement clip whose range covers t_min
    target_clip = None
    for ac in arr_clips:
        clip_start = ac.start_time if hasattr(ac, "start_time") else 0.0
        clip_end = ac.end_time if hasattr(ac, "end_time") else (clip_start + ac.length)
        if clip_start <= t_min < clip_end:
            target_clip = ac
            break

    if target_clip is None:
        ranges = ["{0}-{1}".format(
            ac.start_time if hasattr(ac, "start_time") else "?",
            ac.end_time if hasattr(ac, "end_time") else "?") for ac in arr_clips]
        raise ValueError(
            "No arrangement clip covers time {0}. Clip ranges: [{1}]".format(
                t_min, ", ".join(ranges)))

    clip_start = target_clip.start_time if hasattr(target_clip, "start_time") else 0.0
    clip_end = target_clip.end_time if hasattr(target_clip, "end_time") else (clip_start + target_clip.length)
    if t_max >= clip_end:
        raise ValueError(
            "Automation point at time {0} exceeds clip end {1}. "
            "All points must fall within clip range [{2}, {3})".format(
                t_max, clip_end, clip_start, clip_end))

    envelope = None
    if hasattr(target_clip, "automation_envelope"):
        envelope = target_clip.automation_envelope(parameter)
    if envelope is None and hasattr(target_clip, "create_automation_envelope"):
        envelope = target_clip.create_automation_envelope(parameter)
    if envelope is None:
        is_mixer = parameter_name.lower() in ("volume", "pan", "panning") or parameter_name.lower().startswith("send")
        hint = (
            " Mixer parameters cannot be automated via arrangement clip envelopes. "
            "Workaround: use create_step_automation on a session clip, then "
            "duplicate_clip_to_arrangement."
        ) if is_mixer else (
            " create_automation_envelope() does not work on arrangement clips for "
            "parameters that haven't been automated before. Workaround: use "
            "create_step_automation on a session clip, then duplicate_clip_to_arrangement."
        )
        raise RuntimeError(
            "Could not get automation envelope for '{0}' on arrangement clip.{1}".format(
                parameter_name, hint)
        )

    if not append and hasattr(envelope, 'clear'):
        try:
            envelope.clear()
        except Exception:
            pass

    resolution, planned_steps = budget_automation_steps(automation_points, resolution)

    # Always route through interpolate_automation: it self-guards (returns points
    # unchanged for pure-hold with no per-point overrides), so per-point
    # "interpolation" overrides are honored even when the curve-global mode is "hold".
    automation_points = interpolate_automation(automation_points, resolution, interpolation)

    deadline = _time.time() + AUTOMATION_WRITE_BUDGET_SECONDS
    written = 0
    last_written_time = None
    for point in automation_points:
        if _time.time() > deadline:
            break
        time_val = max(clip_start, min(clip_end - 0.001, float(point.get("time", 0.0))))
        value = max(parameter.min, min(parameter.max, float(point.get("value", 0.0))))
        envelope.insert_step(time_val, 0.001, value)
        written += 1
        last_written_time = time_val

    result = {
        "parameter": parameter_name,
        "track_index": track_index,
        "points_added": written,
        "points_planned": len(automation_points),
        "partial": written < len(automation_points),
        "resolution_used": resolution,
        # On a partial write, the covered range is [clip_start, last_written_time];
        # points are time-sorted, so a caller can resume past this boundary.
        "last_written_time": last_written_time,
    }
    if verify:
        result["verified"] = verify_automation(envelope, automation_points, parameter.min, parameter.max)
    return result


@command("clear_track_automation", modifying=True, destructive=True)
def clear_track_automation(song, track_index: int, parameter_name: str, start_time: float, end_time: float, device_index: int | None = None, ctrl=None) -> dict:
    """Clear automation for a parameter in an arrangement time range.

    Finds the arrangement clip at the given time range and clears (flattens)
    the automation envelope for the parameter by inserting a constant step
    at the parameter's current value.
    """
    start_time = float(start_time)
    end_time = float(end_time)

    track = get_track(song, track_index)
    parameter = _find_parameter(song, track_index, parameter_name, device_index=device_index)

    if end_time <= start_time:
        msg = "End time must be greater than start time"
        if ctrl:
            ctrl.log_message("Invalid clear range: " + msg)
        raise ValueError(msg)

    if not hasattr(track, "arrangement_clips"):
        raise RuntimeError(
            "Arrangement automation requires Live 11+ (track.arrangement_clips not available)"
        )

    arr_clips = list(track.arrangement_clips)
    if not arr_clips:
        raise ValueError(
            "No arrangement clips on track {0}".format(track_index)
        )

    # Find the arrangement clip that covers start_time
    target_clip = None
    clip_end = None
    for ac in arr_clips:
        clip_start = ac.start_time if hasattr(ac, "start_time") else 0.0
        clip_end = ac.end_time if hasattr(ac, "end_time") else (clip_start + ac.length)
        if clip_start <= start_time < clip_end:
            target_clip = ac
            break
    if target_clip is None:
        ranges = ["{0}-{1}".format(
            ac.start_time if hasattr(ac, "start_time") else "?",
            ac.end_time if hasattr(ac, "end_time") else "?") for ac in arr_clips]
        raise ValueError(
            "No arrangement clip covers time {0}. Clip ranges: [{1}]".format(
                start_time, ", ".join(ranges)))

    # Clamp end_time to clip boundary
    if end_time > clip_end:
        end_time = clip_end

    envelope = None
    if hasattr(target_clip, "automation_envelope"):
        envelope = target_clip.automation_envelope(parameter)
    if envelope is None:
        return {"cleared": False, "parameter": parameter_name, "reason": "No automation envelope found"}

    current_value = parameter.value
    envelope.insert_step(start_time, end_time - start_time, current_value)

    return {
        "parameter": parameter_name,
        "track_index": track_index,
        "cleared_from": start_time,
        "cleared_to": end_time,
    }


@command("delete_time", modifying=True, destructive=True, idempotent=False)
def delete_time(song, start_time: float, end_time: float, ctrl=None) -> dict:
    """Delete a section of time from the arrangement."""
    try:
        start_time = float(start_time)
        end_time = float(end_time)
        if start_time >= end_time:
            raise ValueError("Start time must be less than end time")
        song.delete_time(start_time, end_time - start_time)
        return {
            "deleted_from": start_time,
            "deleted_to": end_time,
            "deleted_length": end_time - start_time,
        }
    except (TypeError, ValueError) as e:
        if ctrl:
            ctrl.log_message("Error deleting time: " + str(e))
        raise
    except Exception as e:
        if ctrl:
            ctrl.log_message("Error deleting time: " + str(e))
        raise


@command("duplicate_time", modifying=True)
def duplicate_time(song, start_time: float, end_time: float, ctrl=None) -> dict:
    """Duplicate a section of time in the arrangement."""
    try:
        start_time = float(start_time)
        end_time = float(end_time)
        if start_time >= end_time:
            raise ValueError("Start time must be less than end time")
        song.duplicate_time(start_time, end_time - start_time)
        return {
            "duplicated_from": start_time,
            "duplicated_to": end_time,
            "duplicated_length": end_time - start_time,
            "pasted_at": end_time,
        }
    except (TypeError, ValueError) as e:
        if ctrl:
            ctrl.log_message("Error duplicating time: " + str(e))
        raise
    except Exception as e:
        if ctrl:
            ctrl.log_message("Error duplicating time: " + str(e))
        raise


@command("insert_silence", modifying=True)
def insert_silence(song, position: float, length: float, ctrl=None) -> dict:
    """Insert silence at a position in the arrangement."""
    try:
        position = float(position)
        length = float(length)
        if length <= 0:
            raise ValueError("Length must be greater than 0")
        song.insert_time(position, length)
        return {"inserted_at": position, "inserted_length": length}
    except (TypeError, ValueError) as e:
        if ctrl:
            ctrl.log_message("Error inserting silence: " + str(e))
        raise
    except Exception as e:
        if ctrl:
            ctrl.log_message("Error inserting silence: " + str(e))
        raise


# --- v4.0: Enhanced automation ---


@command("clear_clip_envelope", modifying=True, destructive=True)
def clear_clip_envelope(song, track_index: int, clip_index: int, parameter_name: str, device_index: int | None = None, ctrl=None) -> dict:
    """Clear automation envelope for a specific parameter using clip.clear_envelope()."""
    track, clip = get_clip(song, track_index, clip_index)
    param = _find_parameter(song, track_index, parameter_name, device_index=device_index)

    if not hasattr(clip, 'clear_envelope'):
        raise NotImplementedError("Clip does not support clear_envelope()")

    clip.clear_envelope(param)
    return {"cleared": True, "parameter": parameter_name, "track_index": track_index, "clip_index": clip_index}


@command("clear_all_clip_envelopes", modifying=True, destructive=True)
def clear_all_clip_envelopes(song, track_index: int, clip_index: int, ctrl=None) -> dict:
    """Clear ALL automation envelopes from a clip."""
    _, clip = get_clip(song, track_index, clip_index)

    if not hasattr(clip, 'clear_all_envelopes'):
        raise NotImplementedError("Clip does not support clear_all_envelopes()")

    clip.clear_all_envelopes()
    return {"cleared_all": True, "track_index": track_index, "clip_index": clip_index, "clip_name": clip.name}


@command("get_clip_automation_value")
def get_clip_automation_value(song, track_index: int, clip_index: int, parameter_name: str, time: float, device_index: int | None = None, ctrl=None) -> dict:
    """Read the automation envelope value at a specific time."""
    track, clip = get_clip(song, track_index, clip_index)
    param = _find_parameter(song, track_index, parameter_name, device_index=device_index)

    if not hasattr(clip, 'automation_envelope'):
        raise RuntimeError("Clip does not support automation envelopes")

    envelope = clip.automation_envelope(param)
    if envelope is None:
        return {"has_automation": False, "parameter": parameter_name}

    time = float(time)
    val = envelope.value_at_time(time)
    return {
        "parameter": parameter_name,
        "time": time,
        "value": round(val, 6),
        "param_min": param.min,
        "param_max": param.max,
    }


@command("get_clip_automation_hires")
def get_clip_automation_hires(song, track_index: int, clip_index: int, parameter_name: str, sample_count: int = 128, device_index: int | None = None, ctrl=None) -> dict:
    """Read automation envelope with configurable sample resolution."""
    track, clip = get_clip(song, track_index, clip_index)
    param = _find_parameter(song, track_index, parameter_name, device_index=device_index)

    if not hasattr(clip, 'automation_envelope'):
        return {"has_automation": False, "parameter": parameter_name, "reason": "Clip does not support automation envelopes"}

    envelope = clip.automation_envelope(param)
    if envelope is None:
        return {"has_automation": False, "parameter": parameter_name}

    sample_count = max(2, min(512, int(sample_count)))
    clip_len = clip.length
    if clip_len <= 0:
        return {"has_automation": False, "parameter": parameter_name, "reason": "Clip has zero length"}

    points = []
    step = clip_len / sample_count
    for i in range(sample_count):
        t = i * step
        try:
            val = envelope.value_at_time(t)
            points.append({"time": round(t, 4), "value": round(val, 4)})
        except Exception as e:
            if ctrl:
                ctrl.log_message("Automation sample at t={0} failed: {1}".format(round(t, 4), e))

    return {
        "has_automation": True,
        "parameter": parameter_name,
        "param_min": param.min,
        "param_max": param.max,
        "clip_length": clip_len,
        "sample_count": sample_count,
        "point_count": len(points),
        "points": points,
    }


@command("create_step_automation", modifying=True)
def create_step_automation(song, track_index: int, clip_index: int, parameter_name: str, steps: list, device_index: int | None = None, ctrl=None) -> dict:
    """Create step (held-value) automation — each step holds its value for a duration.

    Args:
        steps: List of {time, value, duration} dicts. duration > 0 creates a held step.
    """
    track, clip = get_clip(song, track_index, clip_index)
    param = _find_parameter(song, track_index, parameter_name, device_index=device_index)

    if not hasattr(clip, 'automation_envelope'):
        if hasattr(clip, 'create_automation_envelope'):
            envelope = clip.create_automation_envelope(param)
        else:
            raise RuntimeError("Clip does not support automation envelopes")
    else:
        envelope = clip.automation_envelope(param)

    if envelope is None:
        if hasattr(clip, 'create_automation_envelope'):
            envelope = clip.create_automation_envelope(param)
        if envelope is None:
            raise RuntimeError("Could not get automation envelope for parameter '{0}'".format(parameter_name))

    if hasattr(envelope, 'clear'):
        try:
            envelope.clear()
        except Exception:
            pass

    clip_length = clip.length
    for step in steps:
        time_val = float(step.get("time", 0.0))
        time_val = max(0.0, min(clip_length - 0.001, time_val))
        value = float(step.get("value", 0.0))
        duration = float(step.get("duration", 0.0))
        duration = max(0.0, min(clip_length - time_val, duration))
        clamped = max(param.min, min(param.max, value))
        envelope.insert_step(time_val, duration, clamped)

    return {
        "parameter": parameter_name,
        "track_index": track_index,
        "clip_index": clip_index,
        "steps_added": len(steps),
    }
