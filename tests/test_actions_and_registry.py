from gesture_control.actions.base import ActionDispatcher
from gesture_control.gestures.types import ActionCommand, GestureEvent
from gesture_control.mappings.registry import MappingRegistry
from gesture_control.mappings.validator import validate_mappings


def test_registry_resolves_enabled_mapping() -> None:
    registry = MappingRegistry(validate_mappings([{
        "id": "play",
        "gesture": "open_palm",
        "action": "media",
        "parameters": {"key": "play_pause"},
    }]))
    command = registry.command_for(GestureEvent.OPEN_PALM)
    assert command == ActionCommand("media", {"key": "play_pause"})


def test_dispatcher_calls_only_registered_handler() -> None:
    received: list[dict[str, object]] = []
    dispatcher = ActionDispatcher()
    dispatcher.register("test", received.append)
    dispatcher.dispatch(ActionCommand("test", {"value": 1}))
    assert received == [{"value": 1}]
