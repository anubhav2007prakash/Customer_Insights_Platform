"""Retention recommendation engine for churn prediction."""
from __future__ import annotations

from typing import Any


class ChurnRecommendationService:
    def generate(self, customer: dict[str, Any]) -> list[dict[str, Any]]:
        recommendations = []
        if customer.get("days_since_last_purchase", 0) > 60:
            recommendations.append({"type": "Send Discount Offer", "priority": "high"})
        if customer.get("health_score", 0) < 40:
            recommendations.append({"type": "Schedule Sales Call", "priority": "high"})
        if not recommendations:
            recommendations.append({"type": "Personalized Email Campaign", "priority": "medium"})
        return recommendations
