from pathlib import Path

import pytest

from gesture_control.gestures.smoothing import ExponentialSmoother, Hysteresis
from gesture_control.gestures.state_machine import GestureStateMachine
from gesture_control.gestures.types import GestureEvent, GestureSignal, TrackingState
from gesture_control.mappings.profile_manager import ProfileManager, default_profile
from gesture_control.mappings.validator import validate_mapping, validate_mappings


def signal(now: float) -> GestureSignal:
    return GestureSignal(GestureEvent.SCROLL_UP, value=1, confidence=0.9, timestamp=now)


def test_ema_suppresses_a_single_jump() -> None:
    smoother = ExponentialSmoother(alpha=0.25)
    assert smoother.update(0) == 0
    assert smoother.update(4) == pytest.approx(1)
    assert smoother.update(4) == pytest.approx(1.75)


def test_hysteresis_requires_release_threshold() -> None:
    gate = Hysteresis(enter_threshold=0.7, exit_threshold=0.4)
    assert not gate.update(0.6)
    assert gate.update(0.7)
    assert gate.update(0.5)
    assert not gate.update(0.4)


def test_state_machine_requires_hold_and_loses_tracking() -> None:
    machine = GestureStateMachine(activation_hold_seconds=0.3, release_grace_seconds=0.1)
    assert machine.update(signal(0), 0) is TrackingState.ACTIVATING
    assert machine.update(signal(0.2), 0.2) is TrackingState.ACTIVATING
    assert machine.update(signal(0.3), 0.3) is TrackingState.ACTIVE
    assert machine.update(None, 0.35) is TrackingState.RELEASING
    assert machine.update(None, 0.5) is TrackingState.LOST


def test_state_machine_emergency_stop_clears_state() -> None:
    machine = GestureStateMachine()
    machine.update(signal(0), 0)
    machine.emergency_stop()
    assert machine.state is TrackingState.IDLE


def test_mapping_validation_rejects_duplicate_ids() -> None:
    item = {"id": "x", "gesture": "scroll_up", "action": "scroll", "parameters": {}}
    with pytest.raises(ValueError, match="unique"):
        validate_mappings([item, item])


def test_profile_round_trip_and_default(tmp_path: Path) -> None:
    manager = ProfileManager(tmp_path)
    saved = manager.save(default_profile())
    assert saved.name == "Reading.json"
    assert manager.load("Reading")["name"] == "Reading"
    assert manager.ensure_default()["schema_version"] == 1


def test_mapping_rejects_unknown_action() -> None:
    with pytest.raises(ValueError, match="unsupported action"):
        validate_mapping({"id": "x", "gesture": "fist", "action": "shell", "parameters": {}})
