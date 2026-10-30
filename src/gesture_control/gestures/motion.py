from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from .types import GestureEvent, HandObservation, Point


@dataclass(frozen=True)
class MotionConfig:
    swipe_threshold: float = 0.16
    scroll_threshold: float = 0.035
    max_jump: float = 0.35


class MotionDetector:
    """Frame-rate-independent palm motion events with jump rejection."""

    def __init__(self, config: MotionConfig | None = None) -> None:
        self.config = config or MotionConfig()
        self._previous: tuple[Point, float] | None = None

    def update(self, hand: HandObservation) -> GestureEvent:
        center = palm_center(hand)
        current = (center, hand.timestamp)
        previous = self._previous
        self._previous = current
        if previous is None:
            return GestureEvent.NONE
        delta_x = center.x - previous[0].x
        delta_y = center.y - previous[0].y
        distance = hypot(delta_x, delta_y)
        if distance > self.config.max_jump:
            return GestureEvent.NONE
        if abs(delta_x) >= self.config.swipe_threshold and abs(delta_x) > abs(delta_y):
            return GestureEvent.SWIPE_RIGHT if delta_x > 0 else GestureEvent.SWIPE_LEFT
        if abs(delta_y) >= self.config.scroll_threshold and abs(delta_y) > abs(delta_x):
            return GestureEvent.SCROLL_DOWN if delta_y > 0 else GestureEvent.SCROLL_UP
        return GestureEvent.NONE

    def reset(self) -> None:
        self._previous = None


def palm_center(hand: HandObservation) -> Point:
    points = hand.landmarks[0:5] + hand.landmarks[9:13]
    return Point(
        sum(point.x for point in points) / len(points),
        sum(point.y for point in points) / len(points),
        sum(point.z for point in points) / len(points),
    )
