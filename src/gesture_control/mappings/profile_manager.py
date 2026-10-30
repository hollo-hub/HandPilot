from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .validator import Mapping, validate_mappings


SCHEMA_VERSION = 1


def default_profile() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "name": "Reading",
        "settings": {"sensitivity": 1.0, "scroll_speed": 3, "activation_delay": 0.35},
        "mappings": [
            {"id": "scroll-up", "gesture": "scroll_up", "action": "scroll", "parameters": {"steps": 3}},
            {"id": "scroll-down", "gesture": "scroll_down", "action": "scroll", "parameters": {"steps": -3}},
            {"id": "media-toggle", "gesture": "open_palm", "action": "media", "parameters": {"key": "play_pause"}},
            {"id": "volume-up", "gesture": "pinch", "action": "volume", "parameters": {"direction": "up", "steps": 2}},
            {"id": "browser-back", "gesture": "swipe_left", "action": "shortcut", "parameters": {"keys": ["alt", "left"]}},
            {"id": "browser-forward", "gesture": "swipe_right", "action": "shortcut", "parameters": {"keys": ["alt", "right"]}},
        ],
    }


class ProfileManager:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, profile: dict[str, Any]) -> Path:
        validated = self._validate_profile(profile)
        destination = self.directory / f"{validated['name']}.json"
        temporary = destination.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(validated, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, destination)
        return destination

    def load(self, name: str) -> dict[str, Any]:
        path = self.directory / f"{name}.json"
        try:
            profile = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ValueError(f"profile not found: {name}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"profile is not valid JSON: {name}") from exc
        return self._validate_profile(profile)

    def ensure_default(self) -> dict[str, Any]:
        try:
            return self.load("Reading")
        except ValueError:
            profile = default_profile()
            self.save(profile)
            return profile

    @staticmethod
    def _validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(profile, dict) or profile.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unsupported or missing profile schema version")
        name = profile.get("name")
        if not isinstance(name, str) or not name.strip() or Path(name).name != name:
            raise ValueError("profile name must be a safe, non-empty filename")
        mappings = validate_mappings(profile.get("mappings", []))
        settings = profile.get("settings", {})
        if not isinstance(settings, dict):
            raise ValueError("profile settings must be an object")
        return {
            "schema_version": SCHEMA_VERSION,
            "name": name,
            "settings": dict(settings),
            "mappings": [_mapping_to_dict(item) for item in mappings],
        }


def _mapping_to_dict(mapping: Mapping) -> dict[str, Any]:
    return {
        "id": mapping.id,
        "gesture": mapping.gesture,
        "action": mapping.action,
        "parameters": mapping.parameters,
        "enabled": mapping.enabled,
    }
