"""Feature registry service."""
from __future__ import annotations

from typing import Any

from feature_store.catalog.service import FeatureCatalogService


class FeatureRegistryService:
    def __init__(self) -> None:
        self._features: dict[str, dict[str, Any]] = {}

    def register_feature(self, name: str, description: str, category: str, owner: str, source_dataset: str, data_type: str, refresh_frequency: str, tags: list[str] | None = None) -> dict[str, Any]:
        feature_id = f"feature-{len(self._features) + 1}"
        feature = {
            "feature_id": feature_id,
            "name": name,
            "description": description,
            "category": category,
            "owner": owner,
            "source_dataset": source_dataset,
            "data_type": data_type,
            "refresh_frequency": refresh_frequency,
            "status": "draft",
            "tags": tags or [],
        }
        self._features[feature_id] = feature
        FeatureCatalogService().add(feature)
        return feature

    def approve(self, feature_id: str) -> dict[str, Any] | None:
        feature = self._features.get(feature_id)
        if feature is not None:
            feature["status"] = "approved"
        return feature

    def list_features(self) -> list[dict[str, Any]]:
        return list(self._features.values())
