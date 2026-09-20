"""Reusable feature engineering engine."""
from __future__ import annotations

from typing import Any


class FeatureEngineeringService:
    def generate_features(self, rows: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:
        features = []
        for row in rows:
            feature_map: dict[str, Any] = {"category": category}
            if category == "customer":
                feature_map["name"] = "customer_age"
                feature_map["value"] = row.get("age")
                features.append(feature_map)
                features.append({"category": category, "name": "days_since_last_purchase", "value": row.get("days_since_last_purchase")})
                features.append({"category": category, "name": "purchase_frequency", "value": row.get("purchase_count")})
                features.append({"category": category, "name": "average_order_value", "value": row.get("avg_order_value")})
                features.append({"category": category, "name": "total_spend", "value": row.get("total_spend")})
            elif category == "marketing":
                features.append({"category": category, "name": "click_rate", "value": row.get("click_rate")})
            else:
                features.append({"category": category, "name": "base_feature", "value": None})
        return features
