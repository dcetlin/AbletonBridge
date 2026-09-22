"""Tests for read-back verification (verify_automation) and DeferredReadBack.

conftest.py stubs ``_Framework`` so the Remote Script package (and its handlers)
import cleanly off-host — see tests/conftest.py.
"""
import queue

import pytest
from unittest.mock import MagicMock

from AbletonBridge_Remote_Script.handlers._helpers import verify_automation
from AbletonBridge_Remote_Script.handlers.automation import create_clip_automation


class _FakeEnvelope:
    """Envelope double whose value_at_time is driven by a dict or callable."""

    def __init__(self, values):
        self._values = values

    def value_at_time(self, t):
        v = self._values
        if callable(v):
            return v(t)
        return v[t]


class TestVerifyAutomation:
    def test_empty_points_is_trivial_match(self):
        result = verify_automation(_FakeEnvelope({}), [], 0.0, 1.0)
        assert result == {"verdict": "match", "median_error": 0, "max_error": 0, "samples": 0}

    def test_match_when_readback_equals_expected(self):
        points = [{"time": 0.0, "value": 0.2}, {"time": 1.0, "value": 0.5}, {"time": 2.0, "value": 0.8}]
        env = _FakeEnvelope({0.0: 0.2, 1.0: 0.5, 2.0: 0.8})
        result = verify_automation(env, points, 0.0, 1.0)
        assert result["verdict"] == "match"
        assert result["max_error"] == 0
        assert result["samples"] == 3

    def test_drift_when_one_outlier_but_median_tight(self):
        # Two exact points + one large outlier: median error stays 0, max blows past epsilon.
        points = [{"time": 0.0, "value": 0.2}, {"time": 1.0, "value": 0.5}, {"time": 2.0, "value": 0.8}]
        env = _FakeEnvelope({0.0: 0.2, 1.0: 0.5, 2.0: 0.3})  # last point off by 0.5
        result = verify_automation(env, points, 0.0, 1.0)
        assert result["verdict"] == "drift"
        assert result["median_error"] < 0.01
        assert result["max_error"] == pytest.approx(0.5)

    def test_mismatch_when_median_error_exceeds_epsilon(self):
        points = [{"time": 0.0, "value": 0.2}, {"time": 1.0, "value": 0.5}, {"time": 2.0, "value": 0.8}]
        env = _FakeEnvelope({0.0: 0.7, 1.0: 0.0, 2.0: 0.3})  # all points off by >= 0.3
        result = verify_automation(env, points, 0.0, 1.0)
        assert result["verdict"] == "mismatch"
        assert result["median_error"] >= 0.01

    def test_expected_value_is_clamped_to_param_range(self):
        # Expected 2.0 clamps to param_max 1.0; envelope reads back 1.0 -> exact match.
        points = [{"time": 0.0, "value": 2.0}]
        env = _FakeEnvelope({0.0: 1.0})
        result = verify_automation(env, points, 0.0, 1.0)
        assert result["verdict"] == "match"
        assert result["max_error"] == 0

    def test_read_failure_falls_back_to_absolute_expected(self):
        def _boom(_t):
            raise RuntimeError("envelope read failed")

        points = [{"time": 0.0, "value": 0.6}]
        result = verify_automation(_FakeEnvelope(_boom), points, 0.0, 1.0)
        # Error becomes abs(clamped expected) = 0.6 -> well past epsilon -> mismatch.
        assert result["verdict"] == "mismatch"
        assert result["max_error"] == pytest.approx(0.6)


class TestDeferredReadBack:
    """The _deferred_read key must be popped before the handler runs, and its
    read-back result merged into the response under _verified."""

    def _make_bridge(self):
        import AbletonBridge_Remote_Script as rs

        bridge = rs.AbletonBridge.__new__(rs.AbletonBridge)
        bridge.song = lambda: object()  # _song property calls self.song()
        bridge.log_message = lambda *a, **k: None
        # Run scheduled tasks synchronously so the queue is populated in-line.
        bridge.schedule_message = lambda _tick, fn: fn()
        return rs, bridge

    def test_deferred_read_key_is_popped_from_params(self, monkeypatch):
        rs, bridge = self._make_bridge()

        seen = []

        def fake_dispatch(cmd, song, params, ctrl):
            seen.append((cmd, dict(params)))
            return {"points_added": 3}

        monkeypatch.setattr(rs, "dispatch", fake_dispatch)

        params = {
            "track_index": 0,
            "_deferred_read": {"command": "get_clip_automation_value", "params": {"time": 1.0}},
        }
        response = bridge._dispatch_on_main_thread_impl("create_clip_automation", params, "msg")

        # First dispatch = the write; it must NOT have seen the _deferred_read key.
        write_cmd, write_params = seen[0]
        assert write_cmd == "create_clip_automation"
        assert "_deferred_read" not in write_params
        # The caller's params dict was mutated (key popped).
        assert "_deferred_read" not in params

    def test_deferred_read_result_merged_under_verified(self, monkeypatch):
        rs, bridge = self._make_bridge()

        def fake_dispatch(cmd, song, params, ctrl):
            if cmd == "create_clip_automation":
                return {"points_added": 3}
            # The read-back command.
            return {"value": 0.5}

        monkeypatch.setattr(rs, "dispatch", fake_dispatch)

        params = {
            "track_index": 0,
            "_deferred_read": {"command": "get_clip_automation_value", "params": {"time": 1.0}},
        }
        response = bridge._dispatch_on_main_thread_impl("create_clip_automation", params, "msg")

        assert response["status"] == "success"
        assert response["result"]["points_added"] == 3
        assert response["result"]["_verified"] == {"value": 0.5}

    def test_no_deferred_read_leaves_result_untouched(self, monkeypatch):
        rs, bridge = self._make_bridge()

        monkeypatch.setattr(
            rs, "dispatch",
            lambda cmd, song, params, ctrl: {"points_added": 3},
        )

        params = {"track_index": 0}
        response = bridge._dispatch_on_main_thread_impl("create_clip_automation", params, "msg")

        assert response["status"] == "success"
        assert response["result"] == {"points_added": 3}
        assert "_verified" not in response["result"]


def _clip_song(clip_length, readback):
    """Minimal mock song: track 0 / clip 0 with a Volume envelope whose
    value_at_time is driven by ``readback`` (called with the beat time)."""
    envelope = MagicMock()
    envelope.value_at_time.side_effect = readback
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
    track.devices = []
    song = MagicMock()
    song.tracks = [track]
    return song, envelope


class TestVerifyWiredThroughHandler:
    """Integration: verify=True on the real handler, proving it reads back the
    *interpolated* points that were actually written — not the raw breakpoints."""

    def test_hold_mode_verify_reports_match(self):
        song, env = _clip_song(100.0, lambda t: {0.0: 0.2, 1.0: 0.8}[round(t, 6)])
        res = create_clip_automation(
            song, 0, 0, "Volume",
            [{"time": 0.0, "value": 0.2}, {"time": 1.0, "value": 0.8}],
            verify=True,
        )
        assert "verified" in res
        assert res["verified"]["verdict"] == "match"
        assert res["verified"]["samples"] == 2

    def test_verify_absent_when_flag_off(self):
        song, env = _clip_song(100.0, lambda t: 0.0)
        res = create_clip_automation(
            song, 0, 0, "Volume",
            [{"time": 0.0, "value": 0.2}, {"time": 1.0, "value": 0.8}],
        )
        assert "verified" not in res
        env.value_at_time.assert_not_called()

    def test_linear_verify_reads_interpolated_points_not_breakpoints(self):
        # Envelope reads back the ideal linear ramp value at any time.
        song, env = _clip_song(100.0, lambda t: max(0.0, min(1.0, t / 4.0)))
        res = create_clip_automation(
            song, 0, 0, "Volume",
            [{"time": 0.0, "value": 0.0}, {"time": 4.0, "value": 1.0}],
            interpolation="linear", verify=True,
        )
        # More than the 2 breakpoints were verified -> verify used the
        # interpolated expansion, matching what insert_step actually wrote.
        assert res["verified"]["samples"] > 2
        assert res["points_added"] == res["verified"]["samples"]
        assert env.value_at_time.call_count == res["verified"]["samples"]
        assert res["verified"]["verdict"] == "match"
