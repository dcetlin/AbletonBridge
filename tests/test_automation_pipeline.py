"""Tests for automation pipeline: step budgeting, per-point interpolation, Hz conversion."""
import math
import pytest

from AbletonBridge_Remote_Script.handlers._helpers import (
    budget_automation_steps, interpolate_automation,
    MAX_AUTOMATION_STEPS,
)
from MCP_Server.validation import hz_to_normalized, normalized_to_hz


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
