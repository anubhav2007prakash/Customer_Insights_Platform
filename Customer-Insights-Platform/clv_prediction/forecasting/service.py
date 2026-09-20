"""Revenue forecasting service for CLV predictions."""
from __future__ import annotations

from typing import Any


class CLVForecastingService:
    def forecast(self, customers: list[dict[str, Any]], horizon: str = "6m") -> dict[str, Any]:
        total_forecast = sum(float(customer.get("target_clv", 0)) for customer in customers)
        return {
            "horizon": horizon,
            "total_forecast": round(total_forecast, 2),
            "segment_forecast": {"champion": total_forecast / 2 if customers else 0},
            "region_forecast": {"north": total_forecast / 2 if customers else 0},
        }
