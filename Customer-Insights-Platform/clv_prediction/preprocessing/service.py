"""Target generation and preprocessing for CLV modeling."""
from __future__ import annotations

from typing import Any


class CLVPreprocessingService:
    def generate_target(self, customers: list[dict[str, Any]], horizon: str = "6m") -> list[float]:
        horizon_multiplier = {"3m": 1.0, "6m": 1.5, "12m": 2.0, "lt": 3.0}.get(horizon, 1.5)
        targets = []
        for customer in customers:
            targets.append(float(customer.get("target_clv", 0)) * horizon_multiplier)
        return targets
