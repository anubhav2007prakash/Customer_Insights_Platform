"""RFM scoring and categorization service."""
from __future__ import annotations

from typing import Any


class RFMService:
    def score(self, customers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        scored = []
        for customer in customers:
            recency_score = 5 if customer.get("recency", 0) <= 30 else 2
            frequency_score = 5 if customer.get("frequency", 0) >= 5 else 3
            monetary_score = 5 if customer.get("monetary", 0) >= 100 else 2
            rfm_category = "Champions" if (recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4) else "Needs Attention"
            scored.append(
                {
                    "customer_id": customer.get("customer_id"),
                    "recency_score": recency_score,
                    "frequency_score": frequency_score,
                    "monetary_score": monetary_score,
                    "rfm_category": rfm_category,
                }
            )
        return scored
