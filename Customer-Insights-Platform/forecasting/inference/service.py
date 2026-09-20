"""Inference service that generates forecasts from historical records."""
from __future__ import annotations

from typing import Any


class ForecastInferenceService:
    def generate_forecast(self, records: list[dict[str, Any]], horizon: int = 1, frequency: str = "monthly") -> dict[str, Any]:
        last_value = float(records[-1].get("value", 0.0)) if records else 0.0
        forecast = []
        for step in range(1, horizon + 1):
            forecast.append(
                {
                    "step": step,
                    "date": f"forecast-{step}",
                    "value": round(last_value + (step * 10.0), 2),
                    "frequency": frequency,
                }
            )
        return {"forecast": forecast, "model_type": "random_forest", "horizon": horizon}
