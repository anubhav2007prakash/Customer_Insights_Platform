"""Reusable dashboard services for forecasting output."""
from __future__ import annotations

from typing import Any

from forecasting.inference.service import ForecastInferenceService


class ForecastDashboardService:
    def __init__(self) -> None:
        self._inference = ForecastInferenceService()

    def sales_forecast(self, records: list[dict[str, Any]], horizon: int = 1) -> dict[str, Any]:
        return self._inference.generate_forecast(records, horizon=horizon, frequency="monthly")

    def demand_forecast(self, records: list[dict[str, Any]], horizon: int = 1) -> dict[str, Any]:
        return self._inference.generate_forecast(records, horizon=horizon, frequency="monthly")

    def forecast_accuracy(self, records: list[dict[str, Any]]) -> dict[str, float]:
        last_value = float(records[-1].get("value", 0.0)) if records else 0.0
        return {"accuracy": round(min(max(last_value / 100.0, 0.0), 1.0), 2)}
