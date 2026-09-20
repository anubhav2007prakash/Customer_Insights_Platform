"""Monitoring collector for quality and drift metrics."""
from __future__ import annotations

from typing import Dict


class MonitoringCollector:
    def __init__(self):
        self.metrics: Dict[str, dict] = {}

    def record(self, metric_name: str, values: dict) -> None:
        self.metrics[metric_name] = values

    def get_metrics(self) -> Dict[str, dict]:
        return self.metrics
