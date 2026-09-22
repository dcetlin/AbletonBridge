"""Mixer: volume, pan, mute, solo, arm, sends, return tracks, master."""

from __future__ import absolute_import, print_function, unicode_literals
from ._helpers import get_track
from . import devices as dev_mod
from ._registry import command


@command("set_track_volume", modifying=True)
def set_track_volume(song, track_index: int, volume: float, ctrl=None) -> dict:
    """Set track volume."""
    track = get_track(song, track_index)
    volume_param = track.mixer_device.volume
    clamped = max(volume_param.min, min(volume_param.max, volume))
    volume_param.value = clamped
    return {"track_index": track_index, "volume": volume_param.value}


@command("set_track_pan", modifying=True)
def set_track_pan(song, track_index: int, pan: float, ctrl=None) -> dict:
    """Set track panning."""
    track = get_track(song, track_index)
    pan_param = track.mixer_device.panning
    clamped = max(pan_param.min, min(pan_param.max, pan))
    pan_param.value = clamped
    return {"track_index": track_index, "pan": pan_param.value}


@command("set_track_mute", modifying=True)
def set_track_mute(song, track_index: int, mute: bool, ctrl=None) -> dict:
    """Set track mute state."""
    track = get_track(song, track_index)
    track.mute = bool(mute)
    return {"track_index": track_index, "mute": track.mute}


@command("set_track_solo", modifying=True)
def set_track_solo(song, track_index: int, solo: bool, ctrl=None) -> dict:
    """Set track solo state."""
    track = get_track(song, track_index)
    track.solo = bool(solo)
    return {"track_index": track_index, "solo": track.solo}


@command("set_track_arm", modifying=True)
def set_track_arm(song, track_index: int, arm: bool, ctrl=None) -> dict:
    """Set the arm (record enable) state of a track."""
    track = get_track(song, track_index)
    if not track.can_be_armed:
        raise ValueError("Track cannot be armed (group track or no input)")
    track.arm = bool(arm)
    return {"track_index": track_index, "arm": track.arm}


@command("set_track_send", modifying=True)
def set_track_send(song, track_index: int, send_index: int, value: float, ctrl=None) -> dict:
    """Set the send level from a track to a return track."""
    track = get_track(song, track_index)
    sends = track.mixer_device.sends
    if send_index < 0 or send_index >= len(sends):
        raise IndexError("Send index out of range")
    send_param = sends[send_index]
    clamped_value = max(send_param.min, min(send_param.max, value))
    send_param.value = clamped_value
    return {
        "track_index": track_index,
        "send_index": send_index,
        "value": send_param.value,
        "clamped": clamped_value != value,
    }


# --- Return track mixer ---


@command("set_return_track_volume", modifying=True)
def set_return_track_volume(song, return_track_index: int, volume: float, ctrl=None) -> dict:
    """Set the volume of a return track."""
    return_track = get_track(song, return_track_index, "return")
    volume_param = return_track.mixer_device.volume
    clamped = max(volume_param.min, min(volume_param.max, volume))
    volume_param.value = clamped
    return {
        "return_track_index": return_track_index,
        "volume": volume_param.value,
    }


@command("set_return_track_pan", modifying=True)
def set_return_track_pan(song, return_track_index: int, pan: float, ctrl=None) -> dict:
    """Set the panning of a return track."""
    return_track = get_track(song, return_track_index, "return")
    pan_param = return_track.mixer_device.panning
    clamped = max(pan_param.min, min(pan_param.max, pan))
    pan_param.value = clamped
    return {
        "return_track_index": return_track_index,
        "pan": pan_param.value,
    }


@command("set_return_track_mute", modifying=True)
def set_return_track_mute(song, return_track_index: int, mute: bool, ctrl=None) -> dict:
    """Set the mute state of a return track."""
    return_track = get_track(song, return_track_index, "return")
    return_track.mute = bool(mute)
    return {
        "return_track_index": return_track_index,
        "mute": return_track.mute,
    }


@command("set_return_track_solo", modifying=True)
def set_return_track_solo(song, return_track_index: int, solo: bool, ctrl=None) -> dict:
    """Set the solo state of a return track."""
    return_track = get_track(song, return_track_index, "return")
    return_track.solo = bool(solo)
    return {
        "return_track_index": return_track_index,
        "solo": return_track.solo,
    }


# --- Crossfade ---


@command("set_crossfade_assign", modifying=True)
def set_crossfade_assign(song, track_index: int, assign: int, ctrl=None) -> dict:
    """Set A/B crossfade assignment for a track.

    Args:
        assign: 0=NONE, 1=A, 2=B
    """
    track = get_track(song, track_index)
    assign = int(assign)
    if assign not in (0, 1, 2):
        raise ValueError("assign must be 0 (NONE), 1 (A), or 2 (B)")
    track.mixer_device.crossfade_assign = assign
    _labels = {0: "NONE", 1: "A", 2: "B"}
    return {
        "track_index": track_index,
        "track_name": track.name,
        "crossfade_assign": _labels.get(assign, str(assign)),
    }


# --- Crossfader & Track Delay ---


@command("set_crossfader", modifying=True)
def set_crossfader(song, value: float, ctrl=None) -> dict:
    """Set the master crossfader position (0.0=A, 0.5=center, 1.0=B)."""
    cf = song.master_track.mixer_device.crossfader
    clamped = max(cf.min, min(cf.max, float(value)))
    cf.value = clamped
    return {"crossfader": cf.value}


@command("get_crossfader")
def get_crossfader(song, ctrl=None) -> dict:
    """Get the master crossfader position."""
    cf = song.master_track.mixer_device.crossfader
    return {"crossfader": cf.value, "min": cf.min, "max": cf.max}


@command("set_cue_volume", modifying=True)
def set_cue_volume(song, value: float, ctrl=None) -> dict:
    """Set the cue/preview volume."""
    cv = song.master_track.mixer_device.cue_volume
    clamped = max(cv.min, min(cv.max, float(value)))
    cv.value = clamped
    return {"cue_volume": cv.value}


@command("set_track_delay", modifying=True)
def set_track_delay(song, track_index: int, delay: float, ctrl=None) -> dict:
    """Set the track delay compensation in ms."""
    track = get_track(song, track_index)
    td = track.mixer_device.track_delay
    clamped = max(td.min, min(td.max, float(delay)))
    td.value = clamped
    return {"track_index": track_index, "track_delay": td.value}


@command("get_track_delay")
def get_track_delay(song, track_index: int, ctrl=None) -> dict:
    """Get the track delay compensation value."""
    track = get_track(song, track_index)
    td = track.mixer_device.track_delay
    return {"track_index": track_index, "track_delay": td.value,
            "min": td.min, "max": td.max}


@command("set_panning_mode", modifying=True)
def set_panning_mode(song, track_index: int, mode: int, ctrl=None) -> dict:
    """Set the panning mode for a track.

    Args:
        mode: 0=Stereo, 1=Split Stereo
    """
    track = get_track(song, track_index)
    mode = int(mode)
    track.mixer_device.panning_mode = mode
    return {"track_index": track_index, "panning_mode": mode}


@command("set_split_stereo_pan", modifying=True)
def set_split_stereo_pan(song, track_index: int, left: float | None = None, right: float | None = None, ctrl=None) -> dict:
    """Set split stereo pan values (when panning_mode is Split Stereo)."""
    track = get_track(song, track_index)
    changes = {"track_index": track_index}
    if left is not None:
        lp = track.mixer_device.left_split_stereo
        lp.value = max(lp.min, min(lp.max, float(left)))
        changes["left_split_stereo"] = lp.value
    if right is not None:
        rp = track.mixer_device.right_split_stereo
        rp.value = max(rp.min, min(rp.max, float(right)))
        changes["right_split_stereo"] = rp.value
    return changes


# --- Master track ---


@command("get_master_track_info")
def get_master_track_info(song, ctrl=None) -> dict:
    """Get detailed information about the master track."""
    master = song.master_track
    devices = []
    for device_index, device in enumerate(master.devices):
        devices.append({
            "index": device_index,
            "name": device.name,
            "class_name": device.class_name,
            "type": dev_mod.get_device_type(device, ctrl),
        })
    return {
        "name": "Master",
        "volume": master.mixer_device.volume.value,
        "panning": master.mixer_device.panning.value,
        "devices": devices,
    }


@command("set_master_volume", modifying=True)
def set_master_volume(song, volume: float, ctrl=None) -> dict:
    """Set the volume of the master track."""
    master = song.master_track
    volume_param = master.mixer_device.volume
    clamped_value = max(volume_param.min, min(volume_param.max, volume))
    volume_param.value = clamped_value
    return {
        "volume": volume_param.value,
        "clamped": clamped_value != volume,
    }


# --- Read-only info ---


@command("get_scenes")
def get_scenes(song, ctrl=None) -> dict:
    """Get information about all scenes."""
    scenes = []
    for i, scene in enumerate(song.scenes):
        scenes.append({
            "index": i,
            "name": scene.name,
            "tempo": scene.tempo if hasattr(scene, 'tempo') else None,
            "is_triggered": scene.is_triggered if hasattr(scene, 'is_triggered') else False,
            "color_index": scene.color_index if hasattr(scene, 'color_index') else 0,
        })
    return {"scenes": scenes, "count": len(scenes)}


@command("get_return_tracks")
def get_return_tracks(song, ctrl=None) -> dict:
    """Get information about all return tracks."""
    return_tracks = []
    for i, track in enumerate(song.return_tracks):
        devices = []
        for device_index, device in enumerate(track.devices):
            devices.append({
                "index": device_index,
                "name": device.name,
                "class_name": device.class_name,
                "type": dev_mod.get_device_type(device, ctrl),
            })
        sends = []
        for send_index, send in enumerate(track.mixer_device.sends):
            sends.append({
                "index": send_index,
                "name": send.name if hasattr(send, 'name') else "Send " + chr(65 + send_index),
                "value": send.value,
            })
        return_tracks.append({
            "index": i,
            "name": track.name,
            "volume": track.mixer_device.volume.value,
            "panning": track.mixer_device.panning.value,
            "mute": track.mute,
            "solo": track.solo,
            "devices": devices,
            "sends": sends,
        })
    return {"return_tracks": return_tracks, "count": len(return_tracks)}


@command("get_return_track_info")
def get_return_track_info(song, return_track_index: int, ctrl=None) -> dict:
    """Get detailed information about a specific return track."""
    track = get_track(song, return_track_index, "return")
    devices = []
    for device_index, device in enumerate(track.devices):
        devices.append({
            "index": device_index,
            "name": device.name,
            "class_name": device.class_name,
            "type": dev_mod.get_device_type(device, ctrl),
        })
    sends = []
    for send_index, send in enumerate(track.mixer_device.sends):
        sends.append({
            "index": send_index,
            "name": send.name if hasattr(send, 'name') else "Send " + chr(65 + send_index),
            "value": send.value,
        })
    return {
        "index": return_track_index,
        "name": track.name,
        "volume": track.mixer_device.volume.value,
        "panning": track.mixer_device.panning.value,
        "mute": track.mute,
        "solo": track.solo,
        "devices": devices,
        "sends": sends,
    }
