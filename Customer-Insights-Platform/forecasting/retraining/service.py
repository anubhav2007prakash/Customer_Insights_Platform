"""Retraining workflow service for forecasting models."""
from __future__ import annotations

from typing import Any


class RetrainingService:
    def trigger_retraining(self, records: list[dict[str, Any]], strategy: str = "performance") -> dict[str, Any]:
        return {"status": "scheduled", "strategy": strategy, "records": len(records)}
