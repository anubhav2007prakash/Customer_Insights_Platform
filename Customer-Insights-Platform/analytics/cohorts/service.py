"""Cohort generation utilities."""
from __future__ import annotations

from typing import Any


class CohortService:
    def generate(self, records: list[dict[str, Any]], group_by: str = "signup_month") -> list[dict[str, Any]]:
        cohorts: dict[str, int] = {}
        for record in records:
            key = record.get(group_by) or "unknown"
            cohorts[key] = cohorts.get(key, 0) + 1

        return [
            {"group": key, "count": value}
            for key, value in sorted(cohorts.items())
        ]
