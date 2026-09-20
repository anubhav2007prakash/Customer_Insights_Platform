"""Searchable feature catalog."""
from __future__ import annotations

from typing import Any


class FeatureCatalogService:
    _shared_items: list[dict[str, Any]] = []

    def __init__(self) -> None:
        self._items = self.__class__._shared_items

    def add(self, feature: dict[str, Any]) -> None:
        if feature not in self._items:
            self._items.append(feature)

    def search(self, category: str | None = None, owner: str | None = None, tags: list[str] | None = None, source_dataset: str | None = None) -> list[dict[str, Any]]:
        results = []
        for item in self._items:
            if category and item.get("category") != category:
                continue
            if owner and item.get("owner") != owner:
                continue
            if source_dataset and item.get("source_dataset") != source_dataset:
                continue
            if tags and not set(tags).issubset(set(item.get("tags", []))):
                continue
            results.append(item)
        return results
