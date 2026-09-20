"""Simple metrics collector for ETL pipelines."""
from __future__ import annotations

from typing import Dict, Any
import time


class MetricsCollector:
    def __init__(self):
        self._store: Dict[str, Any] = {}

    def record(self, run_id: str, metrics: Dict[str, Any]):
        metrics["timestamp"] = time.time()
        self._store[run_id] = metrics

    def get(self, run_id: str):
        return self._store.get(run_id)
