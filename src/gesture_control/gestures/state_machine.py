from __future__ import annotations

from dataclasses import dataclass

from .types import GestureEvent, GestureSignal, TrackingState


@dataclass
class GestureStateMachine:
    activation_hold_seconds: float = 0.35
    release_grace_seconds: float = 0.18
    cooldown_seconds: float = 0.35
    state: TrackingState = TrackingState.IDLE
    _candidate_since: float | None = None
    _release_since: float | None = None
    _cooldown_until: float | None = None

    def __post_init__(self) -> None:
        if min(
            self.activation_hold_seconds,
            self.release_grace_seconds,
            self.cooldown_seconds,
        ) < 0:
            raise ValueError("state machine durations cannot be negative")

    def update(self, signal: GestureSignal | None, now: float) -> TrackingState:
        if signal is None or signal.event is GestureEvent.NONE:
            return self._lost_or_releasing(now)
        if self._cooldown_until is not None and now < self._cooldown_until:
            self.state = TrackingState.COOLDOWN
            return self.state
        if self._cooldown_until is not None:
            self._cooldown_until = None

        self._release_since = None
        if self.state in {TrackingState.IDLE, TrackingState.LOST, TrackingState.RELEASING}:
            self.state = TrackingState.ACTIVATING
            if self._candidate_since is None:
                self._candidate_since = now
        if self.state is TrackingState.ACTIVATING:
            candidate_since = self._candidate_since
            if candidate_since is not None and (
                now - candidate_since >= self.activation_hold_seconds - 1e-9
            ):
                self.state = TrackingState.ACTIVE
            return self.state
        return self.state

    def complete_event(self, now: float) -> None:
        self.state = TrackingState.COOLDOWN
        self._candidate_since = None
        self._release_since = None
        self._cooldown_until = now + self.cooldown_seconds

    def emergency_stop(self) -> None:
        self.state = TrackingState.IDLE
        self._candidate_since = None
        self._release_since = None
        self._cooldown_until = None

    def _lost_or_releasing(self, now: float) -> TrackingState:
        self._candidate_since = None
        if self.state is TrackingState.ACTIVE:
            self.state = TrackingState.RELEASING
            self._release_since = now
        if self.state is TrackingState.RELEASING:
            release_since = self._release_since
            if release_since is not None and (
                now - release_since >= self.release_grace_seconds - 1e-9
            ):
                self.state = TrackingState.LOST
        elif self.state is TrackingState.ACTIVATING:
            self.state = TrackingState.LOST
        return self.state
