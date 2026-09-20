"""Reusable feature engineering service."""
from __future__ import annotations

from typing import Any


class FeatureEngineeringService:
    def build_features(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        features: list[dict[str, Any]] = []
        for row in rows:
            purchase_count = float(row.get("purchase_count", 0))
            avg_order_value = float(row.get("avg_order_value", 0))
            days_since_last_purchase = float(row.get("days_since_last_purchase", 0))
            features.append(
                {
                    "customer_id": row.get("customer_id"),
                    "purchase_frequency": purchase_count,
                    "average_order_value": avg_order_value,
                    "customer_age_band": "young" if days_since_last_purchase < 30 else "mature",
                    "days_since_last_purchase": days_since_last_purchase,
                }
            )
        return features
