"""Tests for ADSR and LFO curve builder point generation math."""
import math
from unittest.mock import MagicMock, patch

import pytest

from MCP_Server.tools.automation import build_adsr_points, build_lfo_points
from MCP_Server.validation import MAX_AUTOMATION_POINTS


# ---------------------------------------------------------------------------
# ADSR envelope
# ---------------------------------------------------------------------------

class TestADSRPoints:
    def test_basic_structure(self):
        pts = build_adsr_points(attack=1, decay=1, sustain_level=0.5, release=1)
        assert pts[0] == {"time": 0.0, "value": 0.0, "interpolation": "ease_out"}
        assert pts[1] == {"time": 1.0, "value": 1.0, "interpolation": "exponential"}
        assert pts[2] == {"time": 2.0, "value": 0.5, "interpolation": "exponential"}
        assert pts[3] == {"time": 3.0, "value": 0.0}
        assert len(pts) == 4

    def test_with_sustain_hold(self):
        pts = build_adsr_points(
            attack=1, decay=1, sustain_level=0.5, release=1, sustain_time=2,
        )
        assert len(pts) == 5
        assert pts[2] == {"time": 2.0, "value": 0.5, "interpolation": "hold"}
        assert pts[3] == {"time": 4.0, "value": 0.5, "interpolation": "exponential"}
        assert pts[4] == {"time": 5.0, "value": 0.0}

    def test_custom_peak_and_floor(self):
        pts = build_adsr_points(
            attack=1, decay=1, sustain_level=0.6, release=1,
            peak=0.8, floor=0.1,
        )
        assert pts[0]["value"] == 0.1
        assert pts[1]["value"] == 0.8
        assert pts[-1]["value"] == 0.1

    def test_zero_attack(self):
        pts = build_adsr_points(attack=0, decay=1, sustain_level=0.5, release=1)
        assert pts[0]["time"] == 0.0
        assert pts[0]["value"] == 0.0
        assert pts[1]["time"] == 0.0
        assert pts[1]["value"] == 1.0

    def test_zero_decay(self):
        pts = build_adsr_points(attack=1, decay=0, sustain_level=0.5, release=1)
        assert pts[1]["time"] == 1.0
        assert pts[1]["value"] == 1.0
        assert pts[2]["time"] == 1.0
        assert pts[2]["value"] == 0.5

    def test_zero_release(self):
        pts = build_adsr_points(attack=1, decay=1, sustain_level=0.5, release=0)
        assert pts[-1]["time"] == pts[-2]["time"]
        assert pts[-1]["value"] == 0.0

    def test_total_time(self):
        pts = build_adsr_points(
            attack=0.5, decay=0.3, sustain_level=0.7, release=0.2, sustain_time=1.0,
        )
        assert abs(pts[-1]["time"] - 2.0) < 1e-9

    def test_interpolation_modes(self):
        pts = build_adsr_points(
            attack=1, decay=1, sustain_level=0.5, release=1, sustain_time=1,
        )
        modes = [p.get("interpolation") for p in pts]
        assert modes == ["ease_out", "exponential", "hold", "exponential", None]

    def test_no_sustain_time_skips_hold(self):
        pts = build_adsr_points(attack=1, decay=1, sustain_level=0.5, release=1)
        modes = [p.get("interpolation") for p in pts]
        assert "hold" not in modes

    def test_sustain_time_zero_skips_hold(self):
        pts = build_adsr_points(
            attack=1, decay=1, sustain_level=0.5, release=1, sustain_time=0,
        )
        modes = [p.get("interpolation") for p in pts]
        assert "hold" not in modes

    def test_negative_attack_raises(self):
        with pytest.raises(ValueError, match="attack must be non-negative"):
            build_adsr_points(attack=-1, decay=1, sustain_level=0.5, release=1)

    def test_negative_decay_raises(self):
        with pytest.raises(ValueError, match="decay must be non-negative"):
            build_adsr_points(attack=1, decay=-2, sustain_level=0.5, release=1)

    def test_negative_release_raises(self):
        with pytest.raises(ValueError, match="release must be non-negative"):
            build_adsr_points(attack=1, decay=1, sustain_level=0.5, release=-1)

    def test_negative_sustain_time_raises(self):
        with pytest.raises(ValueError, match="sustain_time must be non-negative"):
            build_adsr_points(attack=1, decay=1, sustain_level=0.5, release=1,
                              sustain_time=-1)

    def test_peak_out_of_range_raises(self):
        with pytest.raises(ValueError, match="peak must be between"):
            build_adsr_points(attack=1, decay=1, sustain_level=0.5, release=1, peak=99)

    def test_floor_out_of_range_raises(self):
        with pytest.raises(ValueError, match="floor must be between"):
            build_adsr_points(attack=1, decay=1, sustain_level=0.5, release=1, floor=-0.1)

    def test_sustain_level_out_of_range_raises(self):
        with pytest.raises(ValueError, match="sustain_level must be between"):
            build_adsr_points(attack=1, decay=1, sustain_level=5.0, release=1)


# ---------------------------------------------------------------------------
# LFO waveform
# ---------------------------------------------------------------------------

class TestLFOPoints:
    def test_sine_range(self):
        pts = build_lfo_points("sine", beats=4, resolution=0.25)
        values = [p["value"] for p in pts]
        assert min(values) >= 0.0 - 1e-9
        assert max(values) <= 1.0 + 1e-9

    def test_sine_period(self):
        pts = build_lfo_points("sine", beats=4, cycles=1, resolution=0.25)
        values = [p["value"] for p in pts]
        assert abs(values[0] - 0.5) < 0.01
        peak_idx = max(range(len(values)), key=lambda i: values[i])
        assert abs(pts[peak_idx]["time"] - 1.0) < 0.3

    def test_sine_custom_range(self):
        pts = build_lfo_points("sine", beats=4, min_val=0.2, max_val=0.8, resolution=0.25)
        values = [p["value"] for p in pts]
        assert min(values) >= 0.2 - 1e-9
        assert max(values) <= 0.8 + 1e-9

    def test_triangle_peaks(self):
        pts = build_lfo_points("triangle", beats=4, cycles=1, resolution=0.25)
        values = [p["value"] for p in pts]
        assert abs(values[0] - 0.0) < 0.01
        mid_idx = len(values) // 2
        assert abs(values[mid_idx] - 1.0) < 0.15

    def test_saw_ramp(self):
        pts = build_lfo_points("saw", beats=4, cycles=1, resolution=0.5)
        values = [p["value"] for p in pts]
        # Saw ramps 0→~1 then wraps to 0 at cycle boundary
        assert abs(values[0] - 0.0) < 0.01
        assert values[-2] > 0.8  # near-end is close to 1
        # Values increase monotonically within the cycle (before wrap)
        for i in range(len(values) - 2):
            assert values[i + 1] >= values[i] - 0.01

    def test_square_values(self):
        pts = build_lfo_points("square", beats=4, cycles=1, resolution=0.25)
        values = [p["value"] for p in pts]
        for v in values:
            assert v == pytest.approx(0.0) or v == pytest.approx(1.0)

    def test_square_uses_hold_interpolation(self):
        pts = build_lfo_points("square", beats=4, resolution=0.5)
        for p in pts[:-1]:
            assert p["interpolation"] == "hold"

    def test_smooth_shapes_use_linear(self):
        for shape in ("sine", "triangle", "saw"):
            pts = build_lfo_points(shape, beats=4, resolution=0.5)
            for p in pts[:-1]:
                assert p["interpolation"] == "linear", f"{shape}: expected linear"

    def test_last_point_no_interpolation(self):
        for shape in ("sine", "triangle", "saw", "square"):
            pts = build_lfo_points(shape, beats=4, resolution=0.5)
            assert "interpolation" not in pts[-1]

    def test_random_in_range(self):
        pts = build_lfo_points("random", beats=4, min_val=0.3, max_val=0.7, resolution=0.5)
        for p in pts:
            assert 0.3 - 1e-9 <= p["value"] <= 0.7 + 1e-9

    def test_random_uses_hold(self):
        pts = build_lfo_points("random", beats=4, resolution=0.5)
        for p in pts[:-1]:
            assert p["interpolation"] == "hold"

    def test_phase_offset_sine(self):
        pts_no_offset = build_lfo_points("sine", beats=4, phase_offset=0.0, resolution=0.25)
        pts_offset = build_lfo_points("sine", beats=4, phase_offset=0.25, resolution=0.25)
        assert abs(pts_no_offset[0]["value"] - 0.5) < 0.01
        assert abs(pts_offset[0]["value"] - 1.0) < 0.01

    def test_multiple_cycles(self):
        pts = build_lfo_points("sine", beats=4, cycles=2, resolution=0.125)
        values = [p["value"] for p in pts]
        # 2 cycles → should have peaks above and troughs below midpoint multiple times
        peaks_above = sum(1 for v in values if v > 0.9)
        troughs_below = sum(1 for v in values if v < 0.1)
        assert peaks_above >= 2
        assert troughs_below >= 2

    def test_point_count(self):
        pts = build_lfo_points("sine", beats=4, resolution=0.5)
        assert len(pts) == 9  # 4/0.5 + 1

    def test_invalid_shape_raises(self):
        with pytest.raises(ValueError, match="Unknown shape"):
            build_lfo_points("wobble", beats=4)

    def test_zero_beats_raises(self):
        with pytest.raises(ValueError, match="beats must be positive"):
            build_lfo_points("sine", beats=0)

    def test_negative_beats_raises(self):
        with pytest.raises(ValueError, match="beats must be positive"):
            build_lfo_points("sine", beats=-1)

    def test_point_count_capped_at_max(self):
        pts = build_lfo_points("sine", beats=1000, resolution=0.0625)
        assert len(pts) <= MAX_AUTOMATION_POINTS

    def test_high_cycles_gets_adequate_sampling(self):
        pts = build_lfo_points("sine", beats=1, cycles=30, resolution=0.0625)
        # 30 cycles × 8 min samples/cycle = 240 minimum points
        assert len(pts) >= 240

    def test_seed_deterministic(self):
        pts1 = build_lfo_points("random", beats=4, resolution=0.5, seed=42)
        pts2 = build_lfo_points("random", beats=4, resolution=0.5, seed=42)
        v1 = [p["value"] for p in pts1]
        v2 = [p["value"] for p in pts2]
        assert v1 == v2

    def test_seed_different_values(self):
        pts1 = build_lfo_points("random", beats=4, resolution=0.5, seed=1)
        pts2 = build_lfo_points("random", beats=4, resolution=0.5, seed=2)
        v1 = [p["value"] for p in pts1]
        v2 = [p["value"] for p in pts2]
        assert v1 != v2

    def test_excessive_cycles_raises_not_aliases(self):
        """When cycles * 8 > MAX_AUTOMATION_POINTS, reject instead of aliasing."""
        with pytest.raises(ValueError, match="Cannot render .* cycles without aliasing"):
            build_lfo_points("sine", beats=1, cycles=5000)

    def test_cap_and_nyquist_boundary(self):
        """At the cap boundary, Nyquist contract still holds."""
        max_cycles = (MAX_AUTOMATION_POINTS - 1) // 8
        pts = build_lfo_points("sine", beats=4, cycles=max_cycles, resolution=0.0625)
        assert len(pts) >= max_cycles * 8
        assert len(pts) <= MAX_AUTOMATION_POINTS


# ---------------------------------------------------------------------------
# Integration: verify tools send correct command
# ---------------------------------------------------------------------------

class TestToolIntegration:
    @pytest.mark.asyncio
    async def test_adsr_sends_create_clip_automation(self, patch_ableton):
        patch_ableton.send_command.return_value = {
            "status": "success", "points_added": 5,
        }
        from MCP_Server.tools.automation import register_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_tools(mcp)

        tool_fn = None
        for t in mcp._tool_manager._tools.values():
            if t.name == "generate_adsr_automation":
                tool_fn = t.fn
                break
        assert tool_fn is not None

        result = await tool_fn(
            ctx=MagicMock(),
            track_index=0, clip_index=0, parameter_name="Volume",
            attack=1.0, decay=0.5, sustain_level=0.6, release=1.0,
        )
        call_args = patch_ableton.send_command.call_args
        assert call_args[0][0] == "create_clip_automation"
        params = call_args[0][1]
        assert params["parameter_name"] == "Volume"
        assert len(params["automation_points"]) == 4

    @pytest.mark.asyncio
    async def test_lfo_sends_create_clip_automation(self, patch_ableton):
        patch_ableton.send_command.return_value = {
            "status": "success", "points_added": 17,
        }
        from MCP_Server.tools.automation import register_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_tools(mcp)

        tool_fn = None
        for t in mcp._tool_manager._tools.values():
            if t.name == "generate_lfo_automation":
                tool_fn = t.fn
                break
        assert tool_fn is not None

        result = await tool_fn(
            ctx=MagicMock(),
            track_index=0, clip_index=0, parameter_name="Filter",
            shape="sine", beats=4.0,
        )
        call_args = patch_ableton.send_command.call_args
        assert call_args[0][0] == "create_clip_automation"
        params = call_args[0][1]
        assert params["parameter_name"] == "Filter"
        assert len(params["automation_points"]) > 0
