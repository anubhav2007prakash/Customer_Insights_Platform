"""Scoring service for recommendation personalization."""
from __future__ import annotations

from typing import Any


class ScoringService:
    def score(self, customer: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
        score = float(candidate.get("score", 0.0))
        if customer.get("segment") == "champion":
            score += 0.1
        if customer.get("clv", 0) > 5000:
            score += 0.05
        priority = "high" if score >= 0.9 else "medium" if score >= 0.7 else "low"
        return {
            **candidate,
            "recommendation_score": round(score, 2),
            "confidence_score": round(min(score + 0.05, 0.99), 2),
            "priority": priority,
            "recommendation_type": "product",
            "source_strategy": "rule_based",
        }
