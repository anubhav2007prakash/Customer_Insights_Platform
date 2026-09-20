"""Feature store for reusable ML features."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FeatureDefinition:
    name: str
    description: str
    data_type: str
    source: str
    version: str
    owner: str
    refresh_strategy: str = "on_demand"
    last_updated: str = "unknown"


class FeatureStore:
    def __init__(self) -> None:
        self._features: dict[str, FeatureDefinition] = {}

    def register_feature(self, name: str, description: str, data_type: str, source: str, version: str, owner: str) -> FeatureDefinition:
        feature = FeatureDefinition(name=name, description=description, data_type=data_type, source=source, version=version, owner=owner)
        self._features[name] = feature
        return feature

    def get_feature(self, name: str) -> FeatureDefinition | None:
        return self._features.get(name)
