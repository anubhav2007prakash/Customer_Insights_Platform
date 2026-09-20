"""Scenario simulation service for forecasting."""
from __future__ import annotations

from typing import Any


class ScenarioSimulationService:
    def generate_scenarios(self, records: list[dict[str, Any]], horizon: int = 1) -> list[dict[str, Any]]:
        base_value = float(records[-1].get("value", 0.0)) if records else 0.0
        return [
            {"name": "best_case", "multiplier": 1.2, "forecast_value": round(base_value * 1.2, 2), "horizon": horizon},
            {"name": "expected_case", "multiplier": 1.0, "forecast_value": round(base_value, 2), "horizon": horizon},
            {"name": "worst_case", "multiplier": 0.8, "forecast_value": round(base_value * 0.8, 2), "horizon": horizon},
        ]
