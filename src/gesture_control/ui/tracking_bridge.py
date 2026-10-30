from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Signal

from gesture_control.gestures.types import GestureEvent, TrackingState


class TrackingBridge(QObject):
    """Converts worker callbacks into queued Qt signals for the UI thread."""

    status_changed = Signal(object, str)
    frame_received = Signal(object)
    gesture_received = Signal(object)

    def status_callback(self, state: TrackingState, message: str) -> None:
        self.status_changed.emit(state, message)

    def frame_callback(self, frame: Any) -> None:
        self.frame_received.emit(frame)

    def gesture_callback(self, event: GestureEvent) -> None:
        self.gesture_received.emit(event)
