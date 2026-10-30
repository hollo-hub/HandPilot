from __future__ import annotations

import time
from collections.abc import Callable
from threading import Event, Thread
from typing import Any

from gesture_control.gestures.poses import classify_pose
from gesture_control.gestures.state_machine import GestureStateMachine
from gesture_control.gestures.types import GestureEvent, GestureSignal, TrackingState

from .capture import CameraCapture
from .hand_tracker import HandTracker


class TrackingWorker:
    """Owns the camera/tracker lifecycle outside the Qt UI thread."""

    def __init__(
        self,
        capture: CameraCapture,
        tracker: HandTracker,
        state_machine: GestureStateMachine | None = None,
        on_status: Callable[[TrackingState, str], None] | None = None,
        on_frame: Callable[[Any], None] | None = None,
        on_event: Callable[[GestureEvent], None] | None = None,
    ) -> None:
        self.capture = capture
        self.tracker = tracker
        self.state_machine = state_machine or GestureStateMachine()
        self.on_status = on_status
        self.on_frame = on_frame
        self.on_event = on_event
        self._stop = Event()
        self._thread: Thread | None = None
        self._last_frame_timestamp: float | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return
        self.capture.start()
        try:
            self.tracker.start()
        except Exception:
            self.capture.stop()
            raise
        self._stop.clear()
        self._last_frame_timestamp = None
        self._thread = Thread(target=self._run, name="gesture-tracking", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None:
            thread.join(timeout=2)
        self._thread = None
        self.state_machine.emergency_stop()
        self.tracker.close()
        self.capture.stop()
        self._notify(TrackingState.IDLE, "Tracking stopped")

    def emergency_stop(self) -> None:
        self.state_machine.emergency_stop()
        self._notify(TrackingState.IDLE, "Emergency stop")

    def _run(self) -> None:
        self._notify(TrackingState.IDLE, "Camera active; looking for a hand")
        while not self._stop.is_set():
            frame = self.capture.read_latest()
            if frame is None:
                time.sleep(0.01)
                continue
            if frame.timestamp == self._last_frame_timestamp:
                time.sleep(0.003)
                continue
            self._last_frame_timestamp = frame.timestamp
            self.on_frame and self.on_frame(frame.image)
            try:
                result = self.tracker.detect(frame.image, frame.timestamp)
            except Exception as exc:
                self._notify(TrackingState.LOST, f"Tracking error: {exc}")
                return
            signal = self._signal(result)
            state = self.state_machine.update(signal, frame.timestamp)
            self._notify(state, _status_text(state, signal))
            if state is TrackingState.ACTIVE and signal is not None and self.on_event:
                self.on_event(signal.event)

    def _signal(self, result: Any) -> GestureSignal | None:
        if not result.hands:
            return None
        hand = max(result.hands, key=lambda item: item.confidence)
        event = classify_pose(hand)
        if event is GestureEvent.NONE:
            return None
        return GestureSignal(event, confidence=hand.confidence, timestamp=result.timestamp)

    def _notify(self, state: TrackingState, message: str) -> None:
        if self.on_status:
            self.on_status(state, message)


def _status_text(state: TrackingState, signal: GestureSignal | None) -> str:
    if signal is not None:
        return f"{state.value}: {signal.event.value}"
    return state.value.replace("_", " ").capitalize()
