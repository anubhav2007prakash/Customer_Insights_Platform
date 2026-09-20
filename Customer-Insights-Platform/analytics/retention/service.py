"""Retention calculation service."""
from __future__ import annotations

from typing import Any


class RetentionService:
    def calculate(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        if not records:
            return {"retention_rate": 0.0, "returning_customers": 0}

        returning = sum(1 for record in records if record.get("returned"))
        return {
            "retention_rate": round(returning / len(records), 4),
            "returning_customers": returning,
        }
