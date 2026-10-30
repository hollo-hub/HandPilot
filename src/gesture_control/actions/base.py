from __future__ import annotations

from collections.abc import Callable

from gesture_control.gestures.types import ActionCommand


class ActionDispatcher:
    """Dispatches validated semantic commands without coupling recognition to OS APIs."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[dict[str, object]], None]] = {}

    def register(self, action: str, handler: Callable[[dict[str, object]], None]) -> None:
        self._handlers[action] = handler

    def dispatch(self, command: ActionCommand) -> None:
        try:
            handler = self._handlers[command.action]
        except KeyError as exc:
            raise ValueError(f"no handler registered for action: {command.action}") from exc
        handler(command.parameters)
