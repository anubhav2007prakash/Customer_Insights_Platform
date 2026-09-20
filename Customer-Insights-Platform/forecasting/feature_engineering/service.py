"""Feature engineering service for forecasting models."""
from __future__ import annotations

from datetime import datetime
from typing import Any


class FeatureEngineeringService:
    def generate_features(self, records: list[dict[str, Any]], horizon: int = 1, frequency: str = "monthly") -> list[dict[str, Any]]:
        features = []
        for index, record in enumerate(records):
            parsed_date = datetime.fromisoformat(record.get("date", "2024-01-01"))
            features.append(
                {
                    "row_id": index,
                    "month": parsed_date.month,
                    "quarter": ((parsed_date.month - 1) // 3) + 1,
                    "day_of_week": parsed_date.weekday(),
                    "value": float(record.get("value", 0.0)),
                    "frequency": frequency,
                    "horizon": horizon,
                    "product": record.get("product", "unknown"),
                    "region": record.get("region", "unknown"),
                }
            )
        return features
