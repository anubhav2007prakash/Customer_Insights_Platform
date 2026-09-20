"""Scoring utilities for customer health, loyalty, and engagement."""
from __future__ import annotations

from typing import Any


class ScoringService:
    def calculate_scores(self, profile: Any) -> dict[str, float]:
        profile_completion = getattr(profile, "profile_completion_pct", 0)
        return {
            "health_score": round(min(100.0, profile_completion), 2),
            "loyalty_score": round(min(100.0, profile_completion + 10), 2),
            "engagement_score": round(min(100.0, profile_completion + 5), 2),
            "satisfaction_score": round(min(100.0, profile_completion + 3), 2),
            "value_score": round(min(100.0, profile_completion + 8), 2),
            "churn_risk_score": round(max(0.0, 100.0 - profile_completion), 2),
            "purchase_intent_score": round(min(100.0, profile_completion + 2), 2),
            "lead_quality_score": round(min(100.0, profile_completion + 4), 2),
        }
