from __future__ import annotations

from gesture_control.gestures.types import ActionCommand, GestureEvent

from .validator import Mapping


class MappingRegistry:
    def __init__(self, mappings: tuple[Mapping, ...]) -> None:
        self._by_gesture = {
            mapping.gesture: mapping for mapping in mappings if mapping.enabled
        }

    def command_for(self, event: GestureEvent) -> ActionCommand | None:
        mapping = self._by_gesture.get(event.value)
        if mapping is None:
            return None
        return ActionCommand(mapping.action, dict(mapping.parameters))
