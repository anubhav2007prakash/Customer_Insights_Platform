"""Monitoring service for model usage metrics."""
from __future__ import annotations

from typing import Any


class MonitoringService:
    def __init__(self) -> None:
        self._prediction_count = 0
        self._latency_total = 0.0
        self._errors = 0

    def record_prediction(self, latency_ms: float, error: bool = False) -> dict[str, Any]:
        self._prediction_count += 1
        self._latency_total += latency_ms
        if error:
            self._errors += 1
        return {
            "prediction_count": self._prediction_count,
            "latency_ms": round(latency_ms, 2),
            "error_rate": round(self._errors / self._prediction_count, 4),
        }
