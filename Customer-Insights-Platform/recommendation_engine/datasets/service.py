"""Dataset preparation for recommendation engine."""
from __future__ import annotations

from typing import Any


class RecommendationDatasetService:
    def prepare_dataset(self, customers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "customer_id": customer.get("customer_id"),
                "segment": customer.get("segment", "unknown"),
                "clv": customer.get("clv", 0),
                "churn_probability": customer.get("churn_probability", 0),
                "health_score": customer.get("health_score", 0),
                "loyalty_score": customer.get("loyalty_score", 0),
                "purchase_history": customer.get("purchase_history", []),
                "preferences": customer.get("preferences", []),
                "products": customer.get("products", []),
            }
            for customer in customers
        ]
