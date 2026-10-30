from __future__ import annotations

from collections.abc import Callable
from typing import Any


def media_action(parameters: dict[str, object]) -> None:
    key = parameters.get("key", "play_pause")
    keys = {
        "play_pause": "play/pause",
        "next": "next",
        "previous": "previous",
    }
    if key not in keys:
        raise ValueError(f"unsupported media key: {key}")
    from pynput.keyboard import Controller, Key

    media_keys: dict[str, Any] = {
        "play_pause": getattr(Key, "media_play_pause", None),
        "next": getattr(Key, "media_next", None),
        "previous": getattr(Key, "media_previous", None),
    }
    selected = media_keys[key]
    if selected is None:
        raise RuntimeError("media key is not available on this platform")
    Controller().press(selected)


def shortcut_action(parameters: dict[str, object]) -> None:
    keys = parameters.get("keys")
    if not isinstance(keys, list) or not keys or not all(isinstance(key, str) for key in keys):
        raise ValueError("shortcut keys must be a non-empty list of strings")
    from pynput.keyboard import Controller, Key

    controller = Controller()
    parsed = [_parse_key(key, Key) for key in keys]
    for key in parsed:
        controller.press(key)
    for key in reversed(parsed):
        controller.release(key)


def volume_action(parameters: dict[str, object]) -> None:
    direction = parameters.get("direction", "up")
    steps = parameters.get("steps", 2)
    if direction not in {"up", "down"} or not isinstance(steps, int) or not 1 <= steps <= 10:
        raise ValueError("volume direction or steps are invalid")
    from pynput.keyboard import Controller, Key

    key = getattr(Key, "media_volume_up" if direction == "up" else "media_volume_down", None)
    if key is None:
        raise RuntimeError("volume keys are not available on this platform")
    controller = Controller()
    for _ in range(steps):
        controller.press(key)


def _parse_key(value: str, key_enum: Any) -> Any:
    named = getattr(key_enum, value, None)
    if named is not None:
        return named
    if len(value) == 1:
        return value
    raise ValueError(f"unsupported shortcut key: {value}")


def register_system_actions(dispatcher: Any) -> None:
    dispatcher.register("media", media_action)
    dispatcher.register("volume", volume_action)
    dispatcher.register("shortcut", shortcut_action)
