"""Automation tool handlers for AbletonBridge."""
import json
import math
import random as _random_mod
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import Context
from MCP_Server.tools._base import _get_tool_annotations, _tool_handler
from MCP_Server.connections.ableton import get_ableton_connection
from MCP_Server.validation import _validate_index, _validate_range, _validate_automation_points, _reduce_automation_points, MAX_AUTOMATION_POINTS


def build_adsr_points(attack, decay, sustain_level, release,
                      peak=1.0, floor=0.0, sustain_time=None):
    """Build ADSR envelope breakpoints with per-point interpolation modes.

    Returns a list of {time, value, interpolation?} dicts ready for
    create_clip_automation's per-point interpolation engine.

    Stages: attack (ease_out), decay (exponential), optional sustain hold,
    release (exponential). Without sustain_time, decay flows directly into release.
    """
    for name, val in [("attack", attack), ("decay", decay), ("release", release)]:
        if val < 0:
            raise ValueError(f"{name} must be non-negative, got {val}")
    if sustain_time is not None and sustain_time < 0:
        raise ValueError(f"sustain_time must be non-negative, got {sustain_time}")
    for name, val in [("peak", peak), ("floor", floor), ("sustain_level", sustain_level)]:
        if not 0.0 <= val <= 1.0:
            raise ValueError(f"{name} must be between 0.0 and 1.0, got {val}")

    points = []
    t = 0.0

    points.append({"time": t, "value": floor, "interpolation": "ease_out"})
    t += attack

    points.append({"time": t, "value": peak, "interpolation": "exponential"})
    t += decay

    if sustain_time is not None and sustain_time > 0:
        points.append({"time": t, "value": sustain_level, "interpolation": "hold"})
        t += sustain_time

    points.append({"time": t, "value": sustain_level, "interpolation": "exponential"})
    t += release

    points.append({"time": t, "value": floor})
    return points


_MIN_SAMPLES_PER_CYCLE = 8


def build_lfo_points(shape, beats, cycles=1.0, min_val=0.0, max_val=1.0,
                     phase_offset=0.0, resolution=0.0625, seed=None):
    """Build LFO waveform sample points with per-point interpolation modes.

    Returns a list of {time, value, interpolation?} dicts.
    Shapes: sine, triangle, saw, square, random.

    Raises ValueError if the cycle count requires more samples than
    MAX_AUTOMATION_POINTS to avoid aliasing. When the resolution alone
    would exceed the budget (but Nyquist is satisfied), resolution is
    coarsened to fit.
    """
    valid_shapes = ("sine", "triangle", "saw", "square", "random")
    if shape not in valid_shapes:
        raise ValueError(f"Unknown shape '{shape}'. Valid: {', '.join(valid_shapes)}")
    if beats <= 0:
        raise ValueError("beats must be positive")

    # Nyquist guard: ensure adequate sampling per cycle
    min_steps_for_cycles = int(math.ceil(cycles * _MIN_SAMPLES_PER_CYCLE))

    # Reject if faithful sampling is impossible within the point budget
    if min_steps_for_cycles + 1 > MAX_AUTOMATION_POINTS:
        max_cycles = (MAX_AUTOMATION_POINTS - 1) // _MIN_SAMPLES_PER_CYCLE
        raise ValueError(
            f"Cannot render {cycles} cycles without aliasing "
            f"(needs {min_steps_for_cycles + 1} points, max {MAX_AUTOMATION_POINTS}). "
            f"Reduce cycles to <= {max_cycles}."
        )

    num_steps = max(min_steps_for_cycles, int(beats / resolution))

    # Cap at MAX_AUTOMATION_POINTS, coarsening resolution if needed
    if num_steps + 1 > MAX_AUTOMATION_POINTS:
        num_steps = MAX_AUTOMATION_POINTS - 1

    if seed is not None:
        rng = _random_mod.Random(seed)
    else:
        rng = _random_mod

    points = []
    for i in range(num_steps + 1):
        t = min(i * (beats / num_steps), beats)
        phase = (t / beats) * cycles + phase_offset
        p = phase % 1.0

        if shape == "sine":
            raw = 0.5 + 0.5 * math.sin(2 * math.pi * phase)
            interp = "linear"
        elif shape == "triangle":
            raw = 2 * p if p < 0.5 else 2 * (1 - p)
            interp = "linear"
        elif shape == "saw":
            raw = p
            interp = "linear"
        elif shape == "square":
            raw = 1.0 if p < 0.5 else 0.0
            interp = "hold"
        else:  # random
            raw = rng.random()
            interp = "hold"

        value = min_val + (max_val - min_val) * raw
        points.append({"time": t, "value": value, "interpolation": interp})

    if points:
        points[-1].pop("interpolation", None)
    return points


def register_tools(mcp):
    @mcp.tool()
    @_tool_handler("creating clip automation")
    def create_clip_automation(ctx: Context, track_index: int, clip_index: int,
                                parameter_name: str, automation_points: List[Dict[str, float]],
                                device_index: Optional[int] = None,
                                reduce: bool = False, append: bool = False,
                                interpolation: str = "hold",
                                resolution: float = 0.0625,
                                verify: bool = False) -> str:
        """Create automation for a parameter within a session clip.

        For automation inside a session clip's envelope. For arrangement-level track
        automation (Volume, Pan, etc. on the timeline), use create_track_automation instead.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - parameter_name: Name of the parameter to automate (e.g., "Osc 1 Pos", "Filter 1 Freq")
        - automation_points: List of {time: float, value: float} dictionaries (breakpoints)
        - device_index: Optional device index to scope parameter lookup
        - reduce: If True, apply RDP point reduction to simplify the curve (default: False)
        - append: If True, add points to existing automation instead of clearing first (default: False)
        - interpolation: Curve shape between breakpoints: "hold" (staircase, default),
          "linear" (smooth ramps), "exponential" (exponential curve)
        - resolution: Beats between interpolated points (default: 0.0625 = 64th note).
          Lower = smoother but more points. Only used when interpolation != "hold".
        - verify: If True, read the envelope back after writing and return a
          {verdict, median_error, max_error, samples} report (default: False)

        Values are in the parameter's native range (usually 0.0–1.0).
        Time is in beats from clip start.
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")
        _validate_automation_points(automation_points)
        if reduce:
            automation_points = _reduce_automation_points(automation_points, max_points=20)
        ableton = get_ableton_connection()
        cmd_params: dict[str, object] = {
            "track_index": track_index,
            "clip_index": clip_index,
            "parameter_name": parameter_name,
            "automation_points": automation_points,
            "append": append,
            "interpolation": interpolation,
            "resolution": resolution,
            "verify": verify,
        }
        if device_index is not None:
            cmd_params["device_index"] = device_index
        result = ableton.send_command("create_clip_automation", cmd_params)
        pts = result.get("points_added", len(automation_points))
        mode_label = f" ({interpolation}, res={resolution})" if interpolation != "hold" else ""
        if verify and result.get("verified"):
            return json.dumps(result)
        return f"Created automation with {pts} points{mode_label} for parameter '{parameter_name}'"

    @mcp.tool()
    @_tool_handler("getting clip automation")
    def get_clip_automation(ctx: Context, track_index: int, clip_index: int,
                            parameter_name: str,
                            device_index: Optional[int] = None) -> str:
        """
        Read existing automation from a clip for a specific parameter.

        Samples the automation envelope at 64 evenly-spaced points across the clip length.

        Parameters:
        - track_index: The index of the track containing the clip
        - clip_index: The index of the clip slot containing the clip
        - parameter_name: Name of the parameter (e.g., "Volume", "Pan", or any device parameter name)
        - device_index: Optional device index to scope parameter lookup
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")
        ableton = get_ableton_connection()
        cmd_params: dict[str, Any] = {
            "track_index": track_index,
            "clip_index": clip_index,
            "parameter_name": parameter_name,
        }
        if device_index is not None:
            cmd_params["device_index"] = device_index
        result = ableton.send_command("get_clip_automation", cmd_params)
        if not result.get("has_automation"):
            reason = result.get("reason", "No automation found")
            return f"No automation for '{parameter_name}': {reason}"
        return json.dumps(result)

    @mcp.tool(annotations=_get_tool_annotations("clear_clip_automation"))
    @_tool_handler("clearing clip automation")
    def clear_clip_automation(ctx: Context, track_index: int, clip_index: int,
                              parameter_name: str) -> str:
        """
        Clear automation for a specific parameter in a clip.

        Parameters:
        - track_index: The index of the track containing the clip
        - clip_index: The index of the clip slot containing the clip
        - parameter_name: Name of the parameter to clear automation for
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")
        ableton = get_ableton_connection()
        result = ableton.send_command("clear_clip_automation", {
            "track_index": track_index,
            "clip_index": clip_index,
            "parameter_name": parameter_name,
        })
        if result.get("cleared"):
            return f"Cleared automation for '{parameter_name}'"
        return f"Could not clear automation for '{parameter_name}': {result.get('reason', 'Unknown')}"

    @mcp.tool()
    @_tool_handler("listing automated parameters")
    def list_clip_automated_parameters(ctx: Context, track_index: int, clip_index: int) -> str:
        """
        List all parameters that have automation in a given clip.

        Parameters:
        - track_index: The index of the track containing the clip
        - clip_index: The index of the clip slot containing the clip
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")
        ableton = get_ableton_connection()
        result = ableton.send_command("list_clip_automated_params", {
            "track_index": track_index,
            "clip_index": clip_index,
        })
        params = result.get("automated_parameters", [])
        if not params:
            return "No automated parameters found in this clip"
        output = f"Found {len(params)} automated parameter(s):\n\n"
        for p in params:
            source = p.get("source", "Unknown")
            output += f"• {p.get('name', '?')} (source: {source})"
            if "device_index" in p:
                output += f" [device {p['device_index']}]"
            output += "\n"
        return output

    @mcp.tool()
    @_tool_handler("creating track automation")
    def create_track_automation(
        ctx: Context,
        track_index: int,
        parameter_name: str,
        automation_points: list,
        device_index: Optional[int] = None,
        reduce: bool = False,
        append: bool = False,
        interpolation: str = "hold",
        resolution: float = 0.0625,
        verify: bool = False,
    ) -> str:
        """Create automation for a track parameter (arrangement-level).

        For arrangement-level automation on the timeline. For automation within a
        session clip's envelope, use create_clip_automation instead.

        Parameters:
        - track_index: The index of the track
        - parameter_name: Name of the parameter to automate (e.g., "Volume", "Pan")
        - automation_points: List of {time: float, value: float} dictionaries (breakpoints)
        - device_index: Optional device index to scope parameter lookup
        - reduce: If True, apply RDP point reduction to simplify the curve (default: False)
        - append: If True, add points to existing automation instead of clearing first (default: False)
        - interpolation: Curve shape between breakpoints: "hold" (staircase, default),
          "linear" (smooth ramps), "exponential" (exponential curve)
        - resolution: Beats between interpolated points (default: 0.0625 = 64th note).
          Only used when interpolation != "hold".
        - verify: If True, read the envelope back after writing and return a
          {verdict, median_error, max_error, samples} report (default: False)
        """
        _validate_index(track_index, "track_index")
        _validate_automation_points(automation_points)
        if reduce:
            automation_points = _reduce_automation_points(automation_points, max_points=20)
        ableton = get_ableton_connection()
        cmd_params: dict[str, object] = {
            "track_index": track_index,
            "parameter_name": parameter_name,
            "automation_points": automation_points,
            "append": append,
            "interpolation": interpolation,
            "resolution": resolution,
            "verify": verify,
        }
        if device_index is not None:
            cmd_params["device_index"] = device_index
        result = ableton.send_command("create_track_automation", cmd_params)
        pts = result.get("points_added", len(automation_points))
        mode_label = f" ({interpolation}, res={resolution})" if interpolation != "hold" else ""
        if verify and result.get("verified"):
            return json.dumps(result)
        return f"Created track automation for '{parameter_name}' with {pts} points{mode_label}"

    @mcp.tool()
    @_tool_handler("clearing track automation")
    def clear_track_automation(
        ctx: Context,
        track_index: int,
        parameter_name: str,
        start_time: float,
        end_time: float,
    ) -> str:
        """Clear automation for a parameter in a time range (arrangement-level).

        Parameters:
        - track_index: The index of the track
        - parameter_name: Name of the parameter to clear automation for
        - start_time: Start time in beats
        - end_time: End time in beats
        """
        _validate_index(track_index, "track_index")
        if start_time >= end_time:
            return "Error: start_time must be less than end_time"
        ableton = get_ableton_connection()
        result = ableton.send_command("clear_track_automation", {
            "track_index": track_index,
            "parameter_name": parameter_name,
            "start_time": start_time,
            "end_time": end_time,
        })
        return f"Cleared automation for '{parameter_name}' from {start_time} to {end_time}"

    @mcp.tool()
    @_tool_handler("creating automation curve")
    def create_automation_curve(ctx: Context, track_index: int, clip_index: int,
                                  parameter_name: str, curve_type: str = "sine",
                                  start_value: float = 0.0, end_value: float = 1.0,
                                  cycles: float = 1.0, points: int = 32) -> str:
        """Generate curved automation for a clip parameter.

        Parameters:
        - track_index: The track index
        - clip_index: The clip slot index
        - parameter_name: Name of the parameter to automate
        - curve_type: "sine", "cosine", "exponential", "logarithmic", "linear", "triangle", "sawtooth", "s_curve", "ease_in", "ease_out", "ease_in_out", "square", "pulse", "random" (default: "sine")
        - start_value: Starting value (0.0-1.0, default: 0.0)
        - end_value: Ending value (0.0-1.0, default: 1.0)
        - cycles: Number of cycles for periodic curves (default: 1.0)
        - points: Number of automation points to generate (default: 32)
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")

        # Get clip length
        ableton = get_ableton_connection()
        clip_info = ableton.send_command("get_clip_info", {
            "track_index": track_index,
            "clip_index": clip_index,
        })
        clip_length = clip_info.get("length", 4.0)

        automation_points = []
        for i in range(points):
            t = i / max(1, points - 1)  # normalized 0..1
            time = t * clip_length

            if curve_type == "linear":
                value = start_value + (end_value - start_value) * t
            elif curve_type == "sine":
                value = start_value + (end_value - start_value) * (0.5 + 0.5 * math.sin(2 * math.pi * cycles * t - math.pi / 2))
            elif curve_type == "cosine":
                value = start_value + (end_value - start_value) * (0.5 - 0.5 * math.cos(2 * math.pi * cycles * t))
            elif curve_type == "exponential":
                value = start_value + (end_value - start_value) * (t ** 2)
            elif curve_type == "logarithmic":
                value = start_value + (end_value - start_value) * math.sqrt(t)
            elif curve_type == "triangle":
                phase = (t * cycles) % 1.0
                tri = 2 * phase if phase < 0.5 else 2 * (1 - phase)
                value = start_value + (end_value - start_value) * tri
            elif curve_type == "sawtooth":
                phase = (t * cycles) % 1.0
                value = start_value + (end_value - start_value) * phase
            elif curve_type == "s_curve":
                # Smooth S-curve (sigmoid-like via cubic Hermite)
                s = t * t * (3 - 2 * t)
                value = start_value + (end_value - start_value) * s
            elif curve_type == "ease_in":
                # Slow start, fast end (cubic)
                value = start_value + (end_value - start_value) * (t ** 3)
            elif curve_type == "ease_out":
                # Fast start, slow end (cubic)
                value = start_value + (end_value - start_value) * (1 - (1 - t) ** 3)
            elif curve_type == "ease_in_out":
                # Slow start and end, fast middle (quintic)
                s = t * t * t * (t * (t * 6 - 15) + 10)
                value = start_value + (end_value - start_value) * s
            elif curve_type == "square":
                # Square wave
                phase = (t * cycles) % 1.0
                value = end_value if phase < 0.5 else start_value
            elif curve_type == "pulse":
                # Pulse wave (25% duty cycle)
                phase = (t * cycles) % 1.0
                value = end_value if phase < 0.25 else start_value
            elif curve_type == "random":
                import random
                value = start_value + (end_value - start_value) * random.random()
            else:
                raise ValueError(f"Unknown curve_type '{curve_type}'")

            value = max(0.0, min(1.0, value))
            automation_points.append({"time": time, "value": value})

        ableton.send_command("create_clip_automation", {
            "track_index": track_index,
            "clip_index": clip_index,
            "parameter_name": parameter_name,
            "automation_points": automation_points,
        })

        return f"Created {curve_type} automation curve ({points} points) for '{parameter_name}' on track {track_index} clip {clip_index}"

    @mcp.tool(annotations=_get_tool_annotations("clear_clip_envelope"))
    @_tool_handler("clearing clip envelope")
    def clear_clip_envelope(ctx: Context, track_index: int, clip_index: int,
                             parameter_name: str) -> str:
        """Clear automation envelope for a specific parameter using clip.clear_envelope().

        Parameters:
        - track_index: The track index
        - clip_index: The clip slot index
        - parameter_name: Name of the parameter whose envelope to clear
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")
        ableton = get_ableton_connection()
        result = ableton.send_command("clear_clip_envelope", {
            "track_index": track_index, "clip_index": clip_index,
            "parameter_name": parameter_name,
        })
        return json.dumps(result)

    @mcp.tool(annotations=_get_tool_annotations("clear_all_clip_envelopes"))
    @_tool_handler("clearing all clip envelopes")
    def clear_all_clip_envelopes(ctx: Context, track_index: int, clip_index: int) -> str:
        """Clear ALL automation envelopes from a clip.

        Parameters:
        - track_index: The track index
        - clip_index: The clip slot index
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")
        ableton = get_ableton_connection()
        result = ableton.send_command("clear_all_clip_envelopes", {
            "track_index": track_index, "clip_index": clip_index,
        })
        return json.dumps(result)

    @mcp.tool()
    @_tool_handler("getting automation value at time")
    def get_clip_automation_value(ctx: Context, track_index: int, clip_index: int,
                                    parameter_name: str, time: float,
                                    device_index: Optional[int] = None) -> str:
        """Read the automation envelope value at a specific time.

        Parameters:
        - track_index: The track index
        - clip_index: The clip slot index
        - parameter_name: Name of the parameter
        - time: Time position in beats to read the value at
        - device_index: Optional device index to scope parameter lookup
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")
        ableton = get_ableton_connection()
        cmd_params: dict[str, Any] = {
            "track_index": track_index, "clip_index": clip_index,
            "parameter_name": parameter_name, "time": time,
        }
        if device_index is not None:
            cmd_params["device_index"] = device_index
        result = ableton.send_command("get_clip_automation_value", cmd_params)
        return json.dumps(result)

    @mcp.tool()
    @_tool_handler("getting hi-res automation")
    def get_clip_automation_hires(ctx: Context, track_index: int, clip_index: int,
                                    parameter_name: str, sample_count: int = 128,
                                    device_index: Optional[int] = None) -> str:
        """Read automation envelope with configurable sample resolution.

        Parameters:
        - track_index: The track index
        - clip_index: The clip slot index
        - parameter_name: Name of the parameter
        - sample_count: Number of sample points (2-512, default: 128)
        - device_index: Optional device index to scope parameter lookup
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")
        ableton = get_ableton_connection()
        cmd_params: dict[str, Any] = {
            "track_index": track_index, "clip_index": clip_index,
            "parameter_name": parameter_name, "sample_count": sample_count,
        }
        if device_index is not None:
            cmd_params["device_index"] = device_index
        result = ableton.send_command("get_clip_automation_hires", cmd_params)
        return json.dumps(result)

    @mcp.tool()
    @_tool_handler("creating step automation")
    def create_step_automation(ctx: Context, track_index: int, clip_index: int,
                                 parameter_name: str, steps: list,
                                 device_index: Optional[int] = None) -> str:
        """Create step (held-value) automation — each step holds its value for a duration.

        Parameters:
        - track_index: The track index
        - clip_index: The clip slot index
        - parameter_name: Name of the parameter to automate
        - steps: List of {time, value, duration} dicts. duration > 0 creates a held step.
        - device_index: Optional device index to scope parameter lookup
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")
        ableton = get_ableton_connection()
        cmd_params: dict[str, Any] = {
            "track_index": track_index, "clip_index": clip_index,
            "parameter_name": parameter_name, "steps": steps,
        }
        if device_index is not None:
            cmd_params["device_index"] = device_index
        result = ableton.send_command("create_step_automation", cmd_params)
        return json.dumps(result)

    @mcp.tool()
    @_tool_handler("generating ADSR automation")
    def generate_adsr_automation(
        ctx: Context,
        track_index: int,
        clip_index: int,
        parameter_name: str,
        attack: float,
        decay: float,
        sustain_level: float,
        release: float,
        peak: float = 1.0,
        floor: float = 0.0,
        sustain_time: Optional[float] = None,
        device_index: Optional[int] = None,
        resolution: float = 0.0625,
    ) -> str:
        """Generate ADSR envelope automation for a clip parameter.

        Builds sparse breakpoints with per-point interpolation curves:
        attack (ease_out), decay (exponential), release (exponential).
        When sustain_time is set, a hold segment is inserted between decay and release;
        otherwise decay flows directly into release.

        Parameters:
        - track_index: The track index
        - clip_index: The clip slot index
        - parameter_name: Name of the parameter to automate
        - attack: Attack time in beats (floor to peak), must be >= 0
        - decay: Decay time in beats (peak to sustain_level), must be >= 0
        - sustain_level: Sustain value (0.0-1.0)
        - release: Release time in beats (sustain_level to floor), must be >= 0
        - peak: Peak value reached at end of attack (0.0-1.0, default: 1.0)
        - floor: Floor value at start and end (0.0-1.0, default: 0.0)
        - sustain_time: Duration of sustain hold in beats (None = no hold phase)
        - device_index: Optional device index to scope parameter lookup
        - resolution: Beats between interpolated points (default: 0.0625)
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")

        points = build_adsr_points(
            attack, decay, sustain_level, release,
            peak=peak, floor=floor, sustain_time=sustain_time,
        )
        _validate_automation_points(points)

        ableton = get_ableton_connection()
        cmd_params: dict[str, Any] = {
            "track_index": track_index,
            "clip_index": clip_index,
            "parameter_name": parameter_name,
            "automation_points": points,
            "interpolation": "hold",
            "resolution": resolution,
        }
        if device_index is not None:
            cmd_params["device_index"] = device_index
        result = ableton.send_command("create_clip_automation", cmd_params)
        total_time = points[-1]["time"]
        pts = result.get("points_added", len(points))
        return (f"Created ADSR envelope for '{parameter_name}': "
                f"A={attack} D={decay} S={sustain_level} R={release} "
                f"({pts} points, {total_time} beats)")

    @mcp.tool()
    @_tool_handler("generating LFO automation")
    def generate_lfo_automation(
        ctx: Context,
        track_index: int,
        clip_index: int,
        parameter_name: str,
        shape: str,
        beats: float,
        cycles: float = 1.0,
        min_val: float = 0.0,
        max_val: float = 1.0,
        phase_offset: float = 0.0,
        device_index: Optional[int] = None,
        resolution: float = 0.0625,
        seed: Optional[int] = None,
    ) -> str:
        """Generate LFO waveform automation for a clip parameter.

        Generates sampled waveform points with per-point interpolation.
        Smooth shapes (sine, triangle, saw) use linear interpolation;
        square and random use hold. Automatically coarsens resolution if the
        point count would exceed the automation limit, and ensures at least
        8 samples per cycle to prevent aliasing.

        Parameters:
        - track_index: The track index
        - clip_index: The clip slot index
        - parameter_name: Name of the parameter to automate
        - shape: Waveform shape: "sine", "triangle", "saw", "square", "random"
        - beats: Total duration in beats
        - cycles: Number of complete waveform cycles (default: 1.0)
        - min_val: Minimum output value (default: 0.0)
        - max_val: Maximum output value (default: 1.0)
        - phase_offset: Phase offset as fraction of cycle, 0.0-1.0 (default: 0.0)
        - device_index: Optional device index to scope parameter lookup
        - resolution: Target beats between sample points (default: 0.0625).
          May be coarsened if the point count would exceed the automation limit,
          or overridden upward for high cycle counts to prevent aliasing.
        - seed: Optional RNG seed for reproducible "random" shape output
        """
        _validate_index(track_index, "track_index")
        _validate_index(clip_index, "clip_index")

        points = build_lfo_points(
            shape, beats, cycles=cycles, min_val=min_val, max_val=max_val,
            phase_offset=phase_offset, resolution=resolution, seed=seed,
        )
        _validate_automation_points(points)

        ableton = get_ableton_connection()
        cmd_params: dict[str, Any] = {
            "track_index": track_index,
            "clip_index": clip_index,
            "parameter_name": parameter_name,
            "automation_points": points,
            "interpolation": "hold",
            "resolution": resolution,
        }
        if device_index is not None:
            cmd_params["device_index"] = device_index
        result = ableton.send_command("create_clip_automation", cmd_params)
        pts = result.get("points_added", len(points))
        return (f"Created {shape} LFO for '{parameter_name}': "
                f"{cycles} cycle(s) over {beats} beats ({pts} points)")
