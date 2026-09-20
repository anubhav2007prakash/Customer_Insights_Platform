"""Freshness monitoring for features."""
from __future__ import annotations

from typing import Any


class FeatureFreshnessService:
    def __init__(self) -> None:
        self._last_refresh: dict[str, dict[str, Any]] = {}

    def update_last_refresh(self, feature_name: str, stale: bool = False) -> dict[str, Any]:
        record = {"feature_name": feature_name, "stale": stale}
        self._last_refresh[feature_name] = record
        return record

    def is_stale(self, feature_name: str) -> bool:
        return self._last_refresh.get(feature_name, {}).get("stale", False)
