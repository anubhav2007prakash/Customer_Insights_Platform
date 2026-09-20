"""Monitoring service for churn prediction performance."""
from __future__ import annotations

from typing import Any


class ChurnMonitoringService:
    def __init__(self) -> None:
        self._metrics_history: list[dict[str, Any]] = []

    def record_metrics(self, metrics: dict[str, Any]) -> None:
        self._metrics_history.append(metrics)

    def get_metrics(self) -> list[dict[str, Any]]:
        return self._metrics_history
