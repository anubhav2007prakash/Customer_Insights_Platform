"""Retraining orchestration for churn models."""
from __future__ import annotations

from typing import Any


class ChurnRetrainingService:
    def schedule_retraining(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "job_id": "retrain-001",
            "trigger": payload.get("trigger", "manual"),
            "status": "scheduled",
        }
