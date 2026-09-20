"""Next Best Action generation service."""
from __future__ import annotations

from typing import Any


class NextBestActionService:
    def generate(self, customer: dict[str, Any]) -> dict[str, Any]:
        if customer.get("churn_probability", 0) > 0.5:
            action_type = "Trigger Customer Success Outreach"
        elif customer.get("clv", 0) > 5000:
            action_type = "Recommend Premium Plan"
        else:
            action_type = "Send Promotional Email"
        return {
            "customer_id": customer.get("customer_id"),
            "action_type": action_type,
            "priority": "high" if customer.get("health_score", 0) > 70 else "medium",
            "reason": "ai_scored",
        }
