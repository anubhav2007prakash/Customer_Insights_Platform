"""Segmentation training service."""
from __future__ import annotations

from typing import Any


class SegmentationTrainingService:
    def train(self, customers: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "cluster_count": 3,
            "random_seed": 42,
            "normalization": True,
            "max_iterations": 100,
        }
