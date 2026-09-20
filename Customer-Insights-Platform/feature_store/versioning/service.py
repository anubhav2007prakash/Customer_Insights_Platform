"""Feature versioning service."""
from __future__ import annotations

from typing import Any


class FeatureVersionService:
    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []

    def create_version(self, feature: dict[str, Any], changes: str) -> dict[str, Any]:
        versioned = dict(feature)
        versioned["version"] = f"v{len(self._history) + 1}"
        versioned["changes"] = changes
        self._history.append(versioned)
        return versioned

    def rollback(self, feature_id: str) -> dict[str, Any] | None:
        for version in reversed(self._history):
            if version.get("feature_id") == feature_id:
                return version
        return None
