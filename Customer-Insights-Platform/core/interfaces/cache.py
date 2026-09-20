"""Cache port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class CachePort(ABC):
    """Abstract cache backend."""

    @abstractmethod
    def get(self, key: str) -> T | None:
        """Retrieve a cached value."""

    @abstractmethod
    def set(self, key: str, value: T, ttl_seconds: int | None = None) -> None:
        """Store a value with optional TTL."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove a cached value."""

    @abstractmethod
    def clear_prefix(self, prefix: str) -> None:
        """Invalidate all keys matching prefix."""
