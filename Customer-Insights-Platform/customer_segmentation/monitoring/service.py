"""Monitoring service for segmentation quality."""
from __future__ import annotations

from typing import Any


class SegmentMonitoringService:
    def __init__(self) -> None:
        self._history: dict[str, list[dict[str, Any]]] = {}

    def monitor(self, assignments: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "assignment_count": len(assignments),
            "segments_active": len({item.get("cluster_id") for item in assignments if item.get("cluster_id") is not None}),
            "status": "healthy",
        }

    def record_growth(self, segment_id: str, growth: int) -> None:
        self._history.setdefault(segment_id, []).append({"growth": growth})

    def get_history(self, segment_id: str) -> list[dict[str, Any]]:
        return self._history.get(segment_id, [])


MonitoringService = SegmentMonitoringService
