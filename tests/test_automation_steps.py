"""Automation handlers, run against an envelope that behaves as Live's does.

Measured in Live 12: insert_step(start, duration, value) covers (start, start + duration],
outside its steps an envelope reads as the parameter's own value, a later step overlays
earlier ones, and a step with no duration is discarded.
"""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import MagicMock

import pytest

from AbletonBridge_Remote_Script.handlers._helpers import (
    read_envelope,
    verify_automation,
    write_automation_steps,
)
from AbletonBridge_Remote_Script.handlers import automation
from AbletonBridge_Remote_Script.handlers.automation import (
    clear_clip_automation,
    create_clip_automation,
    create_step_automation,
    create_track_automation,
    get_arrangement_automation_hires,
    get_clip_automation,
    get_clip_automation_hires,
    get_clip_automation_value,
)

BASE_VALUE = 0.85
CLIP_LENGTH = 4.0


class LiveLikeEnvelope:
    def __init__(self) -> None:
        self.steps: list[tuple[float, float, float]] = []

    def insert_step(self, start: float, duration: float, value: float) -> None:
        if duration > 0:
            self.steps.append((start, start + duration, value))

    def value_at_time(self, t: float) -> float:
        for start, end, value in reversed(self.steps):
            if start < t <= end:
                return value
        return BASE_VALUE


def _param() -> MagicMock:
    param = MagicMock(min=0.0, max=1.0)
    return param


def _clip(envelope: LiveLikeEnvelope, length: float = CLIP_LENGTH, **attributes: Any) -> MagicMock:
    clip = MagicMock(length=length, **attributes)
    clip.automation_envelope.return_value = envelope
    clip.clear_envelope.side_effect = lambda _p: envelope.steps.clear()
    return clip


def _song(envelope: LiveLikeEnvelope, length: float = CLIP_LENGTH) -> tuple[MagicMock, MagicMock]:
    clip = _clip(envelope, length)
    track = MagicMock(devices=[])
    track.clip_slots = [MagicMock(has_clip=True, clip=clip)]
    track.mixer_device.volume = _param()
    song = MagicMock(tracks=[track])
    return song, clip


def _arrangement_song(envelope: LiveLikeEnvelope, start: float, end: float) -> MagicMock:
    clip = _clip(envelope, end - start, start_time=start, end_time=end)
    track = MagicMock(devices=[], arrangement_clips=[clip])
    track.mixer_device.volume = _param()
    return MagicMock(tracks=[track])


def _points(*pairs: tuple[float, float]) -> list[dict[str, float]]:
    return [{"time": t, "value": v} for t, v in pairs]


def _write_clip(points: list[dict[str, float]], envelope: LiveLikeEnvelope | None = None, **kwargs: Any) -> tuple[LiveLikeEnvelope, dict[str, Any]]:
    envelope = envelope or LiveLikeEnvelope()
    song, _ = _song(envelope)
    return envelope, create_clip_automation(song, 0, 0, "Volume", points, verify=True, **kwargs)


class TestClipWrites:
    def test_values_hold_between_points_and_to_the_end(self) -> None:
        envelope, result = _write_clip(_points((1, 0.2), (2, 0.8)))
        assert [read_envelope(envelope, t) for t in (0.5, 1.0, 1.5, 2.0, 3.9)] == [0.2, 0.2, 0.2, 0.8, 0.8]
        assert result["verified"]["verdict"] == "match"

    def test_unsorted_points_are_written_in_time_order(self) -> None:
        envelope, result = _write_clip(_points((2, 0.8), (0, 0.2)))
        assert [read_envelope(envelope, t) for t in (1.0, 3.0)] == [0.2, 0.8]
        assert result["last_written_time"] == 2.0

    def test_a_new_write_replaces_the_whole_clip(self) -> None:
        envelope, _ = _write_clip(_points((0, 0.1)))
        _write_clip(_points((2, 0.5)), envelope)
        assert read_envelope(envelope, 1.0) == 0.5
        assert read_envelope(envelope, 3.0) == 0.5

    def test_append_replaces_only_its_own_range(self) -> None:
        envelope, _ = _write_clip(_points((0, 0.1)))
        _write_clip(_points((1, 0.5), (2, 0.6)), envelope, append=True, resolution=0.25)
        values = [read_envelope(envelope, t) for t in (0.5, 1.5, 2.1, 2.5)]
        assert values == [0.1, 0.5, 0.6, 0.1]

    def test_points_past_the_clip_are_dropped_without_a_spike(self) -> None:
        envelope, result = _write_clip(_points((0, 0.2), (3, 0.4), (8, 1.0)))
        assert read_envelope(envelope, 3.9) == 0.4
        assert envelope.value_at_time(CLIP_LENGTH) == 0.4
        assert result["verified"]["verdict"] == "match"

    def test_last_point_at_one_time_wins_and_verifies(self) -> None:
        envelope, result = _write_clip(_points((1, 0.2), (1, 0.8)))
        assert read_envelope(envelope, 1.0) == 0.8
        assert result["verified"]["verdict"] == "match"
        assert result["verified"]["samples"] == 1

    def test_values_are_clamped_to_the_parameter_range(self) -> None:
        envelope, _ = _write_clip(_points((0, -1), (1, 2)))
        assert [read_envelope(envelope, t) for t in (0.5, 1.5)] == [0.0, 1.0]

    def test_write_stops_at_the_deadline_and_reports_it(self) -> None:
        envelope = LiveLikeEnvelope()
        written, planned = write_automation_steps(envelope, _points((1, 0.2)), 0.0, 4.0, 0.0, 1.0, time.time() - 1)
        assert (written, planned) == ([], 1)

    def test_partial_is_true_only_when_the_deadline_cut_it_short(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(automation, "AUTOMATION_WRITE_BUDGET_SECONDS", -1)
        _, result = _write_clip(_points((1, 0.2), (2, 0.4)))
        assert result["partial"] is True
        assert (result["points_added"], result["points_planned"]) == (0, 2)

    @pytest.mark.parametrize(
        "points",
        [
            pytest.param(_points((0, 0.2), (4, 0.8)), id="point-at-clip-end"),
            pytest.param(_points((1, 0.2), (1, 0.8)), id="points-at-one-time"),
        ],
    )
    def test_complete_writes_are_not_partial(self, points: list[dict[str, float]]) -> None:
        _, result = _write_clip(points)
        assert result["partial"] is False
        assert result["points_added"] == result["points_planned"] == 1

    def test_linear_to_the_clip_end_is_not_partial(self) -> None:
        _, result = _write_clip(_points((0, 0.0), (4, 1.0)), interpolation="linear")
        assert result["partial"] is False

    def test_no_points_in_range_is_an_error_and_keeps_what_was_there(self) -> None:
        envelope, _ = _write_clip(_points((0, 0.1)))
        with pytest.raises(ValueError, match="No automation points"):
            _write_clip(_points((5, 0.2), (6, 0.8)), envelope)
        assert read_envelope(envelope, 1.0) == 0.1

    def test_range_follows_the_clips_length(self) -> None:
        envelope = LiveLikeEnvelope()
        song, _ = _song(envelope, length=8.0)
        create_clip_automation(song, 0, 0, "Volume", _points((0, 0.2), (6, 0.8)))
        assert read_envelope(envelope, 7.9) == 0.8

    def test_append_tail_stops_at_the_clips_end(self) -> None:
        envelope, _ = _write_clip(_points((3.9, 0.5)), append=True, resolution=1.0)
        assert envelope.steps[-1][1] == CLIP_LENGTH

    def test_append_with_no_resolution_still_writes_a_step(self) -> None:
        envelope = LiveLikeEnvelope()
        write_automation_steps(envelope, _points((1, 0.5)), 0.0, 4.0, 0.0, 1.0, time.time() + 5, tail_beats=0)
        assert envelope.steps[-1][1] > 1.0


class TestVerify:
    def test_catches_a_step_that_did_not_hold(self) -> None:
        envelope = LiveLikeEnvelope()
        envelope.insert_step(1.0, 0.001, 0.2)
        written = [{"time": 1.0, "value": 0.2, "until": 2.0}]
        assert verify_automation(envelope, written, 0.0, 1.0)["verdict"] == "mismatch"

    def test_very_close_points_and_the_clip_end_verify_cleanly(self) -> None:
        envelope, result = _write_clip(_points((1, 0.2), (1.00005, 0.8), (3.99995, 0.4)))
        assert result["verified"]["verdict"] == "match"


class TestTrackWrites:
    def test_range_is_the_clips_and_holds_to_its_end(self) -> None:
        envelope = LiveLikeEnvelope()
        song = _arrangement_song(envelope, 16.0, 24.0)
        result = create_track_automation(song, 0, "Volume", _points((17, 0.2), (19, 0.6)), verify=True)
        assert [read_envelope(envelope, t) for t in (16.5, 18.0, 23.5)] == [0.2, 0.2, 0.6]
        assert read_envelope(envelope, 15.0) == BASE_VALUE
        assert result["verified"]["verdict"] == "match"

    def test_append_keeps_the_rest(self) -> None:
        envelope = LiveLikeEnvelope()
        song = _arrangement_song(envelope, 16.0, 24.0)
        create_track_automation(song, 0, "Volume", _points((17, 0.2)), append=True, resolution=0.5)
        assert read_envelope(envelope, 17.25) == 0.2
        assert read_envelope(envelope, 18.0) == BASE_VALUE

    def test_last_written_time_is_reported(self) -> None:
        song = _arrangement_song(LiveLikeEnvelope(), 16.0, 24.0)
        result = create_track_automation(song, 0, "Volume", _points((17, 0.2), (19, 0.6)))
        assert result["last_written_time"] == 19.0

    def test_refused_new_envelope_explains_the_workaround(self) -> None:
        song = _arrangement_song(LiveLikeEnvelope(), 16.0, 24.0)
        clip = song.tracks[0].arrangement_clips[0]
        clip.automation_envelope.return_value = None
        clip.create_automation_envelope.side_effect = RuntimeError("Not a session clip")
        with pytest.raises(RuntimeError, match="duplicate_clip_to_arrangement"):
            create_track_automation(song, 0, "Volume", _points((17, 0.2)))

    def test_no_arrangement_clip_is_an_error_and_creates_nothing(self) -> None:
        song = _arrangement_song(LiveLikeEnvelope(), 16.0, 24.0)
        song.tracks[0].arrangement_clips = []
        with pytest.raises(ValueError, match="No arrangement clips"):
            create_track_automation(song, 0, "Volume", _points((17, 0.2)))
        song.tracks[0].create_arrangement_clip.assert_not_called()


class TestStepTool:
    def _steps(self, steps: list[dict[str, float]]) -> LiveLikeEnvelope:
        envelope = LiveLikeEnvelope()
        song, _ = _song(envelope)
        create_step_automation(song, 0, 0, "Volume", steps)
        return envelope

    def test_duration_is_kept(self) -> None:
        envelope = self._steps([{"time": 1, "value": 0.2, "duration": 1}])
        assert [read_envelope(envelope, t) for t in (0.5, 1.5, 2.5)] == [BASE_VALUE, 0.2, BASE_VALUE]

    def test_missing_duration_holds_to_the_next_step_or_the_end(self) -> None:
        envelope = self._steps([{"time": 2, "value": 0.8}, {"time": 1, "value": 0.2}])
        assert [read_envelope(envelope, t) for t in (1.5, 2.5, 3.9)] == [0.2, 0.8, 0.8]

    def test_step_past_the_clips_end_is_dropped(self) -> None:
        envelope = LiveLikeEnvelope()
        song, _ = _song(envelope)
        result = create_step_automation(song, 0, 0, "Volume", [{"time": 9, "value": 0.5, "duration": 1}])
        assert envelope.steps == [] and result["steps_added"] == 0

    def test_step_duration_is_capped_at_the_clips_end_and_value_clamped(self) -> None:
        envelope = self._steps([{"time": 3, "value": 2, "duration": 9}])
        assert envelope.steps == [(3.0, CLIP_LENGTH, 1.0)]

    def test_very_short_step_keeps_a_valid_duration(self) -> None:
        envelope = self._steps([{"time": 3, "value": 0.5, "duration": 0.0001}])
        assert envelope.steps[0][1] - envelope.steps[0][0] == pytest.approx(0.001)

    def test_envelope_is_fetched_again_after_clearing(self) -> None:
        stale, fresh = LiveLikeEnvelope(), LiveLikeEnvelope()
        song, clip = _song(stale)
        clip.automation_envelope.side_effect = [stale, None]
        clip.create_automation_envelope.return_value = fresh
        create_step_automation(song, 0, 0, "Volume", [{"time": 1, "value": 0.5, "duration": 1}])
        assert stale.steps == [] and len(fresh.steps) == 1

    def test_earlier_automation_is_cleared(self) -> None:
        envelope = LiveLikeEnvelope()
        song, clip = _song(envelope)
        create_step_automation(song, 0, 0, "Volume", [{"time": 0, "value": 0.2, "duration": 4}])
        create_step_automation(song, 0, 0, "Volume", [{"time": 1, "value": 0.8, "duration": 1}])
        assert read_envelope(envelope, 0.5) == BASE_VALUE
        assert clip.clear_envelope.call_count == 2


class TestReads:
    def _written(self) -> tuple[LiveLikeEnvelope, MagicMock]:
        envelope = LiveLikeEnvelope()
        song, _ = _song(envelope)
        create_clip_automation(song, 0, 0, "Volume", _points((0, 0.2), (2, 0.8)))
        return envelope, song

    def test_value_at_a_step_start_counts_that_step(self) -> None:
        _, song = self._written()
        assert get_clip_automation_value(song, 0, 0, "Volume", 2.0)["value"] == 0.8

    def test_value_at_the_clip_end_stays_within_it(self) -> None:
        _, song = self._written()
        assert get_clip_automation_value(song, 0, 0, "Volume", CLIP_LENGTH)["value"] == 0.8

    def test_sampled_reads_count_a_step_starting_at_the_sample(self) -> None:
        _, song = self._written()
        points = get_clip_automation(song, 0, 0, "Volume")["points"]
        assert points[0]["value"] == 0.2
        hires = get_clip_automation_hires(song, 0, 0, "Volume", sample_count=4)["points"]
        assert [p["value"] for p in hires] == [0.2, 0.2, 0.8, 0.8]

    def test_arrangement_read_counts_a_step_starting_at_the_sample(self) -> None:
        envelope = LiveLikeEnvelope()
        envelope.insert_step(0.0, 4.0, 0.2)
        song = _arrangement_song(envelope, 0.0, 4.0)
        assert get_arrangement_automation_hires(song, 0, "Volume", sample_count=4)["points"][0]["value"] == 0.2

    def test_clearing_uses_the_clips_clear(self) -> None:
        envelope, song = self._written()
        assert clear_clip_automation(song, 0, 0, "Volume")["cleared"] is True
        assert envelope.steps == []


class TestTools:
    """What the MCP tools send and return."""

    PARTIAL = {"status": "success", "partial": True, "points_added": 1, "points_planned": 2}
    COMPLETE = {"status": "success", "partial": False, "points_added": 2, "points_planned": 2}

    async def _call(self, name: str, **arguments: Any) -> str:
        from mcp.server.fastmcp import FastMCP

        from MCP_Server.tools.automation import register_tools

        server = FastMCP("test")
        register_tools(server)
        result = await server.call_tool(name, arguments)
        content = result[0] if isinstance(result, tuple) else result
        return content[0].text

    @pytest.mark.parametrize(
        ("name", "arguments"),
        [
            ("create_clip_automation", {"automation_points": _points((0, 0.1), (1, 0.2))}),
            ("create_track_automation", {"automation_points": _points((0, 0.1), (1, 0.2))}),
            ("generate_adsr_automation", {"attack": 1, "decay": 1, "sustain_level": 0.5, "release": 1}),
            ("generate_lfo_automation", {"shape": "sine", "beats": 4.0}),
            ("create_automation_curve", {"curve_type": "linear", "start_value": 0, "end_value": 1, "duration": 4.0}),
        ],
    )
    @pytest.mark.asyncio
    async def test_partial_writes_are_visible_and_complete_ones_are_a_message(
        self, patch_ableton: MagicMock, name: str, arguments: dict[str, Any]
    ) -> None:
        target = {"track_index": 0, "parameter_name": "Volume", **arguments}
        if name != "create_track_automation":
            target["clip_index"] = 0
        patch_ableton.send_command.return_value = self.PARTIAL
        assert '"partial": true' in await self._call(name, **target)
        patch_ableton.send_command.return_value = self.COMPLETE
        assert "Created" in await self._call(name, **target)

    @pytest.mark.parametrize(("shape", "interpolation"), [("linear", "linear"), ("square", "hold"), ("random", "hold")])
    @pytest.mark.asyncio
    async def test_curve_interpolation_follows_its_shape(
        self, patch_ableton: MagicMock, shape: str, interpolation: str
    ) -> None:
        patch_ableton.send_command.return_value = self.COMPLETE
        await self._call(
            "create_automation_curve", track_index=0, clip_index=0, parameter_name="Volume",
            curve_type=shape, start_value=0, end_value=1, duration=4.0,
        )
        assert patch_ableton.send_command.call_args[0][1]["interpolation"] == interpolation

