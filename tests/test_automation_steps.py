"""Automation steps, checked against how Live's envelopes read in practice.

Observed in Live 12: insert_step(start, duration, value) covers (start, start + duration],
and outside its steps an envelope reads as the parameter's existing value.
"""

from __future__ import annotations

import time

import pytest

from AbletonBridge_Remote_Script.handlers._helpers import (
    read_envelope,
    verify_automation,
    write_automation_steps,
)

BASE_VALUE = 0.85


class LiveLikeEnvelope:
    def __init__(self) -> None:
        self.steps: list[tuple[float, float, float]] = []

    def insert_step(self, start: float, duration: float, value: float) -> None:
        assert duration > 0
        self.steps.append((start, start + duration, value))

    def value_at_time(self, t: float) -> float:
        for start, end, value in reversed(self.steps):
            if start < t <= end:
                return value
        return BASE_VALUE


def _write(points: list[dict[str, float]], end: float = 4.0, start: float = 0.0, tail: float | None = None) -> tuple[LiveLikeEnvelope, list[dict[str, float]]]:
    envelope = LiveLikeEnvelope()
    written = write_automation_steps(envelope, points, start, end, 0.0, 1.0, time.time() + 5, tail_beats=tail)
    return envelope, written


def test_values_hold_between_points_and_to_the_end() -> None:
    envelope, _ = _write([{"time": 0, "value": 0.2}, {"time": 2, "value": 0.8}])
    assert read_envelope(envelope, 0.0) == 0.2
    assert read_envelope(envelope, 1.5) == 0.2
    assert read_envelope(envelope, 2.0) == 0.8
    assert read_envelope(envelope, 3.9) == 0.8


def test_read_back_matches_what_was_written() -> None:
    envelope, written = _write([{"time": 0, "value": 0.2}, {"time": 2, "value": 0.8}])
    assert verify_automation(envelope, written, 0.0, 1.0)["verdict"] == "match"


def test_read_back_catches_a_step_that_did_not_hold() -> None:
    envelope = LiveLikeEnvelope()
    envelope.insert_step(1.0, 0.001, 0.2)
    assert verify_automation(envelope, [{"time": 2.0, "value": 0.2}], 0.0, 1.0)["verdict"] == "mismatch"


def test_append_ends_after_its_tail_and_keeps_what_follows() -> None:
    envelope, _ = _write([{"time": 0, "value": 0.2}], tail=0.5)
    assert read_envelope(envelope, 0.25) == 0.2
    assert read_envelope(envelope, 1.0) == BASE_VALUE


def test_arrangement_range_is_respected() -> None:
    envelope, written = _write([{"time": 1, "value": 0.2}, {"time": 50, "value": 0.8}], start=10.0, end=20.0)
    assert [p["time"] for p in written] == [10.0, pytest.approx(19.999)]
    assert read_envelope(envelope, 15.0) == 0.2


def test_values_are_clamped_to_the_parameter_range() -> None:
    _, written = _write([{"time": 0, "value": -1}, {"time": 1, "value": 2}])
    assert [p["value"] for p in written] == [0.0, 1.0]


def test_points_at_the_same_time_keep_a_valid_duration_and_the_last_wins() -> None:
    envelope, _ = _write([{"time": 1, "value": 0.2}, {"time": 1, "value": 0.8}])
    assert read_envelope(envelope, 1.0) == 0.8


def test_write_stops_at_the_deadline() -> None:
    envelope = LiveLikeEnvelope()
    assert write_automation_steps(envelope, [{"time": 0, "value": 0.2}], 0.0, 4.0, 0.0, 1.0, time.time() - 1) == []
    assert envelope.steps == []
