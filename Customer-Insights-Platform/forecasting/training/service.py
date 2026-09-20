"""Training service for forecasting models."""
from __future__ import annotations

from typing import Any


class ForecastTrainingService:
    def train(self, records: list[dict[str, Any]], target: str = "value", model_type: str = "random_forest") -> dict[str, Any]:
        return {
            "model_type": model_type,
            "target": target,
            "status": "trained",
            "train_size": len(records),
        }
