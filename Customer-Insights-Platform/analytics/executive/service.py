"""Executive scorecard calculations."""
from __future__ import annotations

from typing import Any


class ExecutiveScorecardService:
    def generate(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        revenue = sum(float(record.get("revenue", 0)) for record in records)
        customers = len({record.get("customer_id") for record in records if record.get("customer_id")})
        return {
            "revenue": revenue,
            "customers": customers,
            "health_score": round(min(100, revenue / max(1, customers) / 10), 2),
        }
