"""Inference service for predictions."""
from __future__ import annotations

from typing import Any


class InferenceService:
    def predict_single(self, features: dict[str, Any], model: dict[str, Any] | None = None) -> int:
        return 1 if (features.get("income", 0) > 2000) else 0

    def predict_batch(self, features: list[dict[str, Any]], model: dict[str, Any] | None = None) -> list[int]:
        return [self.predict_single(feature, model) for feature in features]
