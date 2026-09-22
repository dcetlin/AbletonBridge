"""Tests for automation pipeline: step budgeting, per-point interpolation, Hz conversion."""
import math
from unittest.mock import MagicMock

import pytest

from AbletonBridge_Remote_Script.handlers._helpers import (
    budget_automation_steps, interpolate_automation,
    MAX_AUTOMATION_STEPS,
)
from AbletonBridge_Remote_Script.handlers.automation import create_clip_automation
from MCP_Server.validation import hz_to_normalized, normalized_to_hz


def _mock_song_with_volume_envelope(clip_length=100.0):
    """Minimal mock song exposing track 0 / clip 0 with a Volume envelope."""
    envelope = MagicMock()
    clip = MagicMock()
    clip.length = clip_length
    clip.automation_envelope.return_value = envelope
    slot = MagicMock()
    slot.has_clip = True
    slot.clip = clip
    param = MagicMock()
    param.min = 0.0
    param.max = 1.0
    track = MagicMock()
    track.clip_slots = [slot]
    track.mixer_device.volume = param
    song = MagicMock()
    song.tracks = [track]
    return song, envelope


class TestStepBudgeting:
    def test_under_limit_unchanged(self):
        points = [{"time": 0, "value": 0}, {"time": 4, "value": 1}]
        res, count = budget_automation_steps(points, 0.0625)
        assert res == 0.0625
        assert count == 64  # 4 / 0.0625

    def test_over_limit_coarsens(self):
        points = [{"time": 0, "value": 0}, {"time": 256, "value": 1}]
        res, count = budget_automation_steps(points, 0.0625)
        assert count == MAX_AUTOMATION_STEPS
        assert res == 256 / MAX_AUTOMATION_STEPS

    def test_single_point(self):
        points = [{"time": 0, "value": 0}]
        res, count = budget_automation_steps(points, 0.0625)
        assert res == 0.0625
        assert count == 1


class TestPerPointInterpolation:
    def test_per_point_override(self):
        points = [
            {"time": 0, "value": 0, "interpolation": "linear"},
            {"time": 1, "value": 1, "interpolation": "hold"},
            {"time": 2, "value": 0.5},
        ]
        result = interpolate_automation(points, resolution=0.5, mode="hold")
        # First segment: linear (overrides hold)
        # Second segment: hold (explicit)
        assert len(result) > 3  # interpolated points exist
        # Check the first interpolated point is between 0 and 1
        mid = next(p for p in result if 0 < p["time"] < 1)
        assert 0 < mid["value"] < 1  # linear interpolation

    def test_ease_in(self):
        points = [
            {"time": 0, "value": 0},
            {"time": 4, "value": 1},
        ]
        result = interpolate_automation(points, resolution=1.0, mode="ease_in")
        # ease_in: slow start, so value at t=1 (frac=0.25) should be < 0.25
        t1 = next(p for p in result if abs(p["time"] - 1.0) < 0.01)
        assert t1["value"] < 0.25

    def test_ease_out(self):
        points = [
            {"time": 0, "value": 0},
            {"time": 4, "value": 1},
        ]
        result = interpolate_automation(points, resolution=1.0, mode="ease_out")
        # ease_out: fast start, so value at t=1 (frac=0.25) should be > 0.25
        t1 = next(p for p in result if abs(p["time"] - 1.0) < 0.01)
        assert t1["value"] > 0.25

    def test_custom_exponent(self):
        points = [
            {"time": 0, "value": 0, "exponent": 1.0},
            {"time": 4, "value": 1},
        ]
        # exponent=1.0 with exponential should give a specific curve
        result = interpolate_automation(points, resolution=2.0, mode="exponential")
        assert len(result) >= 3

    def test_backward_compat_hold(self):
        points = [{"time": 0, "value": 0}, {"time": 4, "value": 1}]
        result = interpolate_automation(points, mode="hold")
        assert result == points  # no interpolation

    def test_exponent_zero_no_crash(self):
        # Regression: exponent=0 made the exponential closed form divide by zero.
        points = [
            {"time": 0, "value": 0, "exponent": 0.0},
            {"time": 4, "value": 1},
        ]
        result = interpolate_automation(points, resolution=1.0, mode="exponential")
        # exponent -> 0 degenerates to linear: value at frac=0.25 is ~0.25
        t1 = next(p for p in result if abs(p["time"] - 1.0) < 0.01)
        assert abs(t1["value"] - 0.25) < 1e-6

    @pytest.mark.parametrize("mode", ["exponential", "ease_in", "ease_out"])
    def test_zero_exponent_degrades_to_linear(self, mode):
        # Regression: exponent=0 must not crash or produce degenerate output in
        # ANY exponent-driven mode; all degrade to linear.
        points = [
            {"time": 0, "value": 0, "exponent": 0.0},
            {"time": 4, "value": 1},
        ]
        result = interpolate_automation(points, resolution=1.0, mode=mode)
        t1 = next(p for p in result if abs(p["time"] - 1.0) < 0.01)
        assert abs(t1["value"] - 0.25) < 1e-6  # linear at frac=0.25

    @pytest.mark.parametrize("mode", ["exponential", "ease_in", "ease_out"])
    def test_negative_exponent_no_crash(self, mode):
        # Regression: ease_in crashed at frac=0 with a negative exponent
        # (0.0 ** -1 -> ZeroDivisionError). All modes must survive.
        points = [
            {"time": 0, "value": 0, "exponent": -1.0},
            {"time": 4, "value": 1},
        ]
        result = interpolate_automation(points, resolution=1.0, mode=mode)
        t1 = next(p for p in result if abs(p["time"] - 1.0) < 0.01)
        assert abs(t1["value"] - 0.25) < 1e-6  # degraded to linear

    def test_hold_global_with_per_point_override(self):
        # Regression: a per-point override must interpolate even when the
        # curve-global mode is the default "hold".
        points = [
            {"time": 0, "value": 0, "interpolation": "linear"},
            {"time": 2, "value": 1},
        ]
        result = interpolate_automation(points, resolution=0.5, mode="hold")
        assert len(result) > 2  # the linear segment was expanded
        mid = next(p for p in result if 0 < p["time"] < 2)
        assert 0 < mid["value"] < 1


class TestHandlerWiring:
    def test_per_point_override_reaches_write_loop(self):
        # Regression for the "dead code through the handler path" concern:
        # a per-point override must interpolate even though create_clip_automation
        # is called with the default interpolation="hold".
        song, envelope = _mock_song_with_volume_envelope()
        points = [
            {"time": 0, "value": 0, "interpolation": "linear"},
            {"time": 2, "value": 1},
        ]
        result = create_clip_automation(
            song, 0, 0, "volume", points, interpolation="hold", resolution=0.5,
        )
        # The linear segment expanded into many steps -> more than the 2 raw points.
        assert envelope.insert_step.call_count > 2
        assert result["points_added"] == envelope.insert_step.call_count
        assert result["partial"] is False

    def test_plain_hold_writes_raw_points(self):
        # Backward compat: no overrides, default hold -> raw points written as-is.
        song, envelope = _mock_song_with_volume_envelope()
        points = [{"time": 0, "value": 0}, {"time": 2, "value": 1}]
        result = create_clip_automation(song, 0, 0, "volume", points)
        assert envelope.insert_step.call_count == 2
        assert result["points_added"] == 2
        assert result["partial"] is False
        # Full (non-partial) write: last_written_time is the final point's time.
        assert result["last_written_time"] == 2.0


class TestHzConversion:
    def test_20hz_is_zero(self):
        assert abs(hz_to_normalized(20.0)) < 0.001

    def test_20khz_is_one(self):
        assert abs(hz_to_normalized(20000.0) - 1.0) < 0.001

    def test_roundtrip(self):
        for hz in [20, 100, 440, 1000, 5000, 10000, 20000]:
            norm = hz_to_normalized(float(hz))
            back = normalized_to_hz(norm)
            assert abs(back - hz) < 0.1, f"Roundtrip failed for {hz}Hz"

    def test_clamps_input(self):
        assert hz_to_normalized(10.0) == hz_to_normalized(20.0)  # clamped to min
        assert hz_to_normalized(30000.0) == hz_to_normalized(20000.0)  # clamped to max
