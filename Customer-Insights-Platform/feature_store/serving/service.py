"""Centralized feature serving service."""
from __future__ import annotations

from typing import Any


class FeatureServingService:
    def get_feature(self, feature_name: str, entity: dict[str, Any]) -> dict[str, Any]:
        return {"name": feature_name, "entity": entity}
