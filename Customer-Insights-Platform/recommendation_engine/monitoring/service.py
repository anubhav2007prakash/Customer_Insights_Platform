"""Monitoring utilities for recommendation performance."""
from __future__ import annotations

from typing import Any


class MonitoringService:
    def __init__(self) -> None:
        self._metrics: list[dict[str, Any]] = []

    def record_metrics(self, metrics: dict[str, Any]) -> dict[str, Any]:
        self._metrics.append(metrics)
        return metrics

    def get_metrics(self) -> list[dict[str, Any]]:
        return self._metrics
