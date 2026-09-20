"""In-memory cache for feature serving."""
from __future__ import annotations

from typing import Any


class FeatureCacheService:
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def set(self, feature_name: str, value: Any) -> None:
        self._store[feature_name] = value

    def get(self, feature_name: str) -> Any:
        return self._store.get(feature_name)
