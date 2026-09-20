"""Simple funnel analysis service."""
from __future__ import annotations

from typing import Any


class FunnelService:
    def generate(self, records: list[dict[str, Any]], stages: list[str]) -> dict[str, Any]:
        totals = []
        for stage in stages:
            count = sum(1 for record in records if record.get(stage))
            totals.append(count)

        conversion_rates = []
        previous = None
        for count in totals:
            if previous is None:
                conversion_rates.append(1.0)
            else:
                conversion_rates.append(round(count / previous, 4) if previous else 0.0)
            previous = count

        return {
            "stages": stages,
            "counts": totals,
            "conversion_rates": conversion_rates,
        }
