"""Label generation and preprocessing for churn prediction."""
from __future__ import annotations

from typing import Any


class ChurnPreprocessingService:
    def generate_labels(self, customers: list[dict[str, Any]], rules: dict[str, Any] | None = None) -> list[int]:
        rules = rules or {}
        inactivity_days = int(rules.get("inactivity_days", 60))
        labels = []
        for customer in customers:
            churn_flag = 1 if (
                customer.get("subscription_status") == "inactive"
                or customer.get("days_since_last_purchase", 0) >= inactivity_days
                or customer.get("days_since_last_login", 0) >= inactivity_days
            ) else 0
            labels.append(churn_flag)
        return labels
