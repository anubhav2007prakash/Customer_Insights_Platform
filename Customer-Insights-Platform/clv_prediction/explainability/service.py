"""Explainability service for CLV predictions."""
from __future__ import annotations

from typing import Any


class CLVExplainabilityService:
    def explain(self, customer: dict[str, Any], prediction: dict[str, Any]) -> str:
        factors = []
        if customer.get("purchase_frequency", 0) > 3:
            factors.append("strong purchase frequency")
        if customer.get("average_order_value", 0) > 150:
            factors.append("high average order value")
        if customer.get("email_engagement", 0) > 0.5:
            factors.append("consistent engagement")
        if not factors:
            factors = ["stable customer behavior"]
        return (
            f"The customer's predicted lifetime value is high due to {', '.join(factors)}."
        )
