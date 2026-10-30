from __future__ import annotations

from math import hypot

from .types import GestureEvent, HandObservation, Point


def classify_pose(hand: HandObservation) -> GestureEvent:
    """Classify conservative static poses; ambiguous hands return NONE."""
    if hand.confidence < 0.5:
        return GestureEvent.NONE
    points = hand.landmarks
    if _is_pinch(points):
        return GestureEvent.PINCH
    fingers = _extended_fingers(points)
    if fingers == 5:
        return GestureEvent.OPEN_PALM
    if fingers == 0:
        return GestureEvent.FIST
    return GestureEvent.NONE


def _is_pinch(points: tuple[Point, ...]) -> bool:
    thumb_tip = points[4]
    index_tip = points[8]
    index_length = hypot(points[8].x - points[5].x, points[8].y - points[5].y)
    return index_length > 0 and hypot(
        thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y
    ) <= index_length * 0.55


def _extended_fingers(points: tuple[Point, ...]) -> int:
    wrist = points[0]
    tips = (4, 8, 12, 16, 20)
    joints = (3, 6, 10, 14, 18)
    count = 0
    for tip, joint in zip(tips[1:], joints[1:]):
        if hypot(points[tip].x - wrist.x, points[tip].y - wrist.y) > hypot(
            points[joint].x - wrist.x, points[joint].y - wrist.y
        ):
            count += 1
    thumb_extended = abs(points[4].x - points[0].x) > abs(points[3].x - points[0].x)
    return count + int(thumb_extended)
