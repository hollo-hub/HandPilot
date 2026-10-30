from pathlib import Path

import pytest

from gesture_control.camera.hand_tracker import HandTracker
from gesture_control.camera.worker import TrackingWorker
from gesture_control.gestures.poses import classify_pose
from gesture_control.gestures.types import HandObservation, Point, GestureEvent, TrackingState
from gesture_control.gestures.motion import MotionDetector


def observation(points: list[Point], confidence: float = 0.9) -> HandObservation:
    return HandObservation.from_sequence(points, "Right", confidence, 1.0)


def test_tracker_rejects_missing_model(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="max_hands"):
        HandTracker(tmp_path / "model.task", max_hands=0)


def test_tracker_reports_missing_model(tmp_path: Path) -> None:
    tracker = HandTracker(tmp_path / "model.task")
    with pytest.raises(RuntimeError, match="not found"):
        tracker.start()


def test_low_confidence_pose_is_ignored() -> None:
    points = [Point(0.0, 0.0) for _ in range(21)]
    assert classify_pose(observation(points, 0.2)) is GestureEvent.NONE


def test_worker_stops_tracker_when_camera_start_fails() -> None:
    class BrokenCapture:
        def start(self) -> None:
            raise RuntimeError("camera unavailable")

        def stop(self) -> None:
            raise AssertionError("tracker cleanup is not needed before camera starts")

    class Tracker:
        def start(self) -> None:
            raise AssertionError("tracker must not start")

        def close(self) -> None:
            raise AssertionError("tracker must not close")

    worker = TrackingWorker(BrokenCapture(), Tracker())
    with pytest.raises(RuntimeError, match="unavailable"):
        worker.start()


def test_worker_emergency_stop_is_visible() -> None:
    class Capture:
        def start(self) -> None: pass
        def stop(self) -> None: pass

    class Tracker:
        def start(self) -> None: pass
        def close(self) -> None: pass

    statuses: list[tuple[TrackingState, str]] = []
    worker = TrackingWorker(
        Capture(),
        Tracker(),
        on_status=lambda state, message: statuses.append((state, message)),
    )
    worker.emergency_stop()
    assert statuses[-1] == (TrackingState.IDLE, "Emergency stop")


def test_motion_detector_rejects_large_tracking_jump() -> None:
    detector = MotionDetector()
    first = observation([Point(0.2, 0.2) for _ in range(21)])
    second = observation([Point(0.9, 0.9) for _ in range(21)])
    detector.update(first)
    assert detector.update(second) is GestureEvent.NONE


def test_pinch_is_thumb_and_index_distance() -> None:
    points = [Point(0.0, 0.0) for _ in range(21)]
    points[3] = Point(0.08, 0.02)
    points[4] = Point(0.02, 0.38)
    points[5] = Point(0.0, 0.2)
    points[6] = Point(0.0, 0.3)
    points[8] = Point(0.0, 0.4)
    assert classify_pose(observation(points)) is GestureEvent.PINCH
