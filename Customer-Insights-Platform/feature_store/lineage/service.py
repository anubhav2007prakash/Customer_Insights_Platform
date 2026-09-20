"""Feature lineage service."""
from __future__ import annotations

from typing import Any


class FeatureLineageService:
    def record(self, feature: dict[str, Any], source_tables: list[str], pipelines: list[str]) -> dict[str, Any]:
        return {
            "feature_id": feature.get("feature_id"),
            "source_tables": source_tables,
            "pipelines": pipelines,
        }
