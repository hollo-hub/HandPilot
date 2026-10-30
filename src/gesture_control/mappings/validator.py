from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SUPPORTED_ACTIONS = frozenset({"scroll", "volume", "media", "shortcut"})
SUPPORTED_GESTURES = frozenset(
    {"scroll_up", "scroll_down", "pinch", "swipe_left", "swipe_right", "open_palm", "fist"}
)


@dataclass(frozen=True)
class Mapping:
    id: str
    gesture: str
    action: str
    parameters: dict[str, Any]
    enabled: bool = True


def validate_mapping(raw: dict[str, Any]) -> Mapping:
    required = {"id", "gesture", "action", "parameters"}
    missing = required - raw.keys()
    if missing:
        raise ValueError(f"mapping is missing: {', '.join(sorted(missing))}")
    mapping_id = raw["id"]
    if not isinstance(mapping_id, str) or not mapping_id.strip():
        raise ValueError("mapping id must be a non-empty string")
    gesture = raw["gesture"]
    action = raw["action"]
    if gesture not in SUPPORTED_GESTURES:
        raise ValueError(f"unsupported gesture: {gesture}")
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(f"unsupported action: {action}")
    if not isinstance(raw["parameters"], dict):
        raise ValueError("mapping parameters must be an object")
    if not isinstance(raw.get("enabled", True), bool):
        raise ValueError("mapping enabled must be a boolean")
    return Mapping(mapping_id, gesture, action, dict(raw["parameters"]), raw.get("enabled", True))


def validate_mappings(raw: list[dict[str, Any]]) -> tuple[Mapping, ...]:
    mappings = tuple(validate_mapping(item) for item in raw)
    ids = [item.id for item in mappings]
    if len(ids) != len(set(ids)):
        raise ValueError("mapping IDs must be unique")
    gestures = [item.gesture for item in mappings if item.enabled]
    if len(gestures) != len(set(gestures)):
        raise ValueError("enabled gesture mappings must not conflict")
    return mappings
