"""Growth metric calculations."""
from __future__ import annotations

from typing import Any


class GrowthService:
    def calculate(self, values: list[dict[str, Any]]) -> dict[str, Any]:
        if not values:
            return {"growth_rate": 0.0, "periods": 0}

        current = float(values[-1].get("value", 0))
        previous = float(values[0].get("value", 0))
        growth_rate = 0.0
        if previous:
            growth_rate = round((current - previous) / previous, 4)
        return {"growth_rate": growth_rate, "periods": len(values)}
