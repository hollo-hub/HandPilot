from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Sequence


class GestureEvent(StrEnum):
    NONE = "none"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    PINCH = "pinch"
    OPEN_PALM = "open_palm"
    FIST = "fist"


class TrackingState(StrEnum):
    IDLE = "idle"
    ACTIVATING = "activating"
    ACTIVE = "active"
    RELEASING = "releasing"
    COOLDOWN = "cooldown"
    LOST = "tracking_lost"


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    z: float = 0.0


@dataclass(frozen=True)
class HandObservation:
    landmarks: tuple[Point, ...]
    handedness: str | None
    confidence: float
    timestamp: float

    @classmethod
    def from_sequence(
        cls,
        landmarks: Sequence[Point],
        handedness: str | None,
        confidence: float,
        timestamp: float,
    ) -> "HandObservation":
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if len(landmarks) != 21:
            raise ValueError("a hand observation requires 21 landmarks")
        return cls(tuple(landmarks), handedness, confidence, timestamp)


@dataclass(frozen=True)
class GestureSignal:
    event: GestureEvent
    value: float = 0.0
    confidence: float = 0.0
    timestamp: float = 0.0


@dataclass(frozen=True)
class ActionCommand:
    action: str
    parameters: dict[str, object]
