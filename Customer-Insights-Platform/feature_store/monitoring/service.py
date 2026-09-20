"""Feature monitoring service."""
from __future__ import annotations

from typing import Any


class FeatureMonitoringService:
    def __init__(self) -> None:
        self._usage: dict[str, int] = {}

    def record_usage(self, feature_name: str) -> dict[str, Any]:
        self._usage[feature_name] = self._usage.get(feature_name, 0) + 1
        return {"feature_name": feature_name, "usage_count": self._usage[feature_name]}
