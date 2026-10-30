from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gesture_control.gestures.types import HandObservation, Point


class HandTrackerError(RuntimeError):
    """Raised when the MediaPipe tracker cannot be configured."""


@dataclass(frozen=True)
class TrackerResult:
    hands: tuple[HandObservation, ...]
    timestamp: float


class HandTracker:
    """MediaPipe Tasks adapter returning app-owned immutable observations."""

    def __init__(
        self,
        model_path: Path,
        max_hands: int = 2,
        min_detection_confidence: float = 0.6,
        min_tracking_confidence: float = 0.6,
    ) -> None:
        if max_hands < 1:
            raise ValueError("max_hands must be positive")
        if not 0 < min_detection_confidence <= 1 or not 0 < min_tracking_confidence <= 1:
            raise ValueError("tracking confidence must be between 0 and 1")
        self.model_path = model_path
        self.max_hands = max_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self._landmarker: Any | None = None

    def start(self) -> None:
        if not self.model_path.is_file():
            raise HandTrackerError(f"MediaPipe model not found: {self.model_path}")
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
        except ImportError as exc:
            raise HandTrackerError("MediaPipe Tasks is required for hand tracking") from exc
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(self.model_path)),
            running_mode=vision.RunningMode.IMAGE,
            num_hands=self.max_hands,
            min_hand_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)

    def close(self) -> None:
        if self._landmarker is not None:
            self._landmarker.close()
            self._landmarker = None

    def detect(self, image: Any, timestamp: float) -> TrackerResult:
        if self._landmarker is None:
            raise HandTrackerError("hand tracker has not been started")
        try:
            import mediapipe as mp
            import cv2
        except ImportError as exc:
            raise HandTrackerError("MediaPipe is required for hand tracking") from exc
        rgb_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
        )
        result = self._landmarker.detect(rgb_image)
        observations: list[HandObservation] = []
        for index, landmarks in enumerate(result.hand_landmarks):
            points = tuple(Point(point.x, point.y, point.z) for point in landmarks)
            handedness = None
            if index < len(result.handedness) and result.handedness[index]:
                handedness = result.handedness[index][0].category_name
            observations.append(
                HandObservation.from_sequence(
                    points,
                    handedness,
                    _confidence(result, index),
                    timestamp,
                )
            )
        return TrackerResult(tuple(observations), timestamp)


def _confidence(result: Any, index: int) -> float:
    if index >= len(result.handedness) or not result.handedness[index]:
        return 0.0
    return float(result.handedness[index][0].score or 0.0)
