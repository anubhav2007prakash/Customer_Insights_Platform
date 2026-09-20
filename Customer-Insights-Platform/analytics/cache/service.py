"""Simple in-memory cache for analytics results."""
from __future__ import annotations

from typing import Any


class CacheService:
    def __init__(self):
        self._store: dict[tuple[str, tuple[tuple[str, Any], ...]], Any] = {}

    def get(self, metric_id: str, filters: dict[str, Any]) -> Any:
        key = (metric_id, tuple(sorted(filters.items())))
        return self._store.get(key)

    def set(self, metric_id: str, filters: dict[str, Any], value: Any) -> None:
        key = (metric_id, tuple(sorted(filters.items())))
        self._store[key] = value
