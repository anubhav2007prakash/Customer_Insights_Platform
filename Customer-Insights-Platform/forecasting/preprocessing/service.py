"""Preprocessing service for forecasting data."""
from __future__ import annotations

from typing import Any


class ForecastPreprocessingService:
    def preprocess(self, dataset: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                **item,
                "value": float(item.get("value", 0.0)),
                "is_missing": item.get("value") is None,
            }
            for item in dataset
        ]
