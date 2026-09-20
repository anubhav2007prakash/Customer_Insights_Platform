"""Inference and prediction service for churn prediction."""
from __future__ import annotations

from typing import Any


class ChurnInferenceService:
    def predict(self, customer: dict[str, Any], model: dict[str, Any] | None = None) -> dict[str, Any]:
        probability = 0.2
        if customer.get("days_since_last_purchase", 0) > 60:
            probability += 0.45
        if customer.get("health_score", 0) < 40:
            probability += 0.25
        if customer.get("engagement_score", 0) < 30:
            probability += 0.1
        probability = min(probability, 0.99)
        if probability >= 0.75:
            risk_level = "Critical"
        elif probability >= 0.5:
            risk_level = "High"
        elif probability >= 0.25:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        return {
            "customer_id": customer.get("customer_id"),
            "churn_probability": round(probability, 4),
            "risk_level": risk_level,
            "confidence_score": round(min(probability + 0.05, 0.99), 4),
            "prediction_timestamp": "2026-07-05T00:00:00Z",
            "model_version": model.get("version", "v1") if model else "v1",
            "prediction_status": "completed",
        }
