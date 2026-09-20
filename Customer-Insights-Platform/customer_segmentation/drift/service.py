"""Drift detection service."""
from __future__ import annotations

from typing import Any


class DriftDetectionService:
    def detect(self, current: list[dict[str, Any]], baseline: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "drift_detected": len(current) != len(baseline),
            "baseline_size": len(baseline),
            "current_size": len(current),
            "severity": "low" if len(current) == len(baseline) else "medium",
        }
