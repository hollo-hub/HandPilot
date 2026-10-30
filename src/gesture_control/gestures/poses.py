from __future__ import annotations

from math import hypot

from .types import GestureEvent, HandObservation, Point


def classify_pose(hand: HandObservation) -> GestureEvent:
    """Classify conservative static poses; ambiguous hands return NONE."""
    if hand.confidence < 0.5:
        return GestureEvent.NONE
    fingers = _extended_fingers(hand.landmarks)
    if fingers == 5:
        return GestureEvent.OPEN_PALM
    if fingers == 0:
        return GestureEvent.FIST
    if fingers == 2 and _index_middle_only(hand.landmarks):
        return GestureEvent.PINCH
    return GestureEvent.NONE


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


def _index_middle_only(points: tuple[Point, ...]) -> bool:
    return (
        points[8].y < points[6].y
        and points[12].y < points[10].y
        and points[16].y > points[14].y
        and points[20].y > points[18].y
    )
