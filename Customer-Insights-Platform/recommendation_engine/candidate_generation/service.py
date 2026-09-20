"""Candidate generation service for recommendations."""
from __future__ import annotations

from typing import Any


class CandidateGenerationService:
    def generate(self, customer: dict[str, Any]) -> list[dict[str, Any]]:
        candidates = []
        for product in customer.get("products", []):
            candidates.append(
                {
                    "product_id": product,
                    "reason": "based_on_purchase_history",
                    "score": 0.8,
                }
            )
        if not candidates:
            candidates.append({"product_id": "default_product", "reason": "fallback", "score": 0.5})
        return candidates
