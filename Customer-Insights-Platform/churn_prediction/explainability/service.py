"""Explainability service for churn prediction."""
from __future__ import annotations

from typing import Any


class ChurnExplainabilityService:
    def explain(self, customer: dict[str, Any], prediction: dict[str, Any]) -> str:
        drivers = []
        if customer.get("days_since_last_purchase", 0) > 60:
            drivers.append("declining purchase frequency")
        if customer.get("email_engagement", 0) < 0.3:
            drivers.append("reduced email engagement")
        if customer.get("health_score", 0) < 40:
            drivers.append("weak customer health")
        if not drivers:
            drivers = ["stable engagement patterns"]
        explanation = (
            f"The customer's churn risk increased primarily due to {', '.join(drivers)}."
        )
        return explanation
