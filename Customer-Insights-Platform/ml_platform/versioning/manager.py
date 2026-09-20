"""Model versioning support."""
from __future__ import annotations

from typing import Any


class ModelVersionManager:
    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []

    def create_version(self, model: dict[str, Any]) -> dict[str, Any]:
        versioned = dict(model)
        versioned["version"] = versioned.get("version") or "v1"
        self._history.append(versioned)
        return versioned

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._history)
