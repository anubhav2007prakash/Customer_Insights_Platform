"""In-memory cache adapter."""

from __future__ import annotations

import time
from typing import Any

from core.interfaces.cache import CachePort


class InMemoryCache(CachePort):
    """Thread-unsafe in-memory cache for development/testing."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float | None]] = {}

    def get(self, key: str) -> Any | None:
        if key not in self._store:
            return None
        value, expires = self._store[key]
        if expires and time.time() > expires:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        expires = time.time() + ttl_seconds if ttl_seconds else None
        self._store[key] = (value, expires)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear_prefix(self, prefix: str) -> None:
        keys = [k for k in self._store if k.startswith(prefix)]
        for k in keys:
            del self._store[k]
