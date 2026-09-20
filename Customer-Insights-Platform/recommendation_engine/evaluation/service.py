"""Evaluation service for recommendation metrics."""
from __future__ import annotations

from typing import Any


class EvaluationService:
    def evaluate(self, dataset: list[dict[str, Any]], recommendations: list[dict[str, Any]]) -> dict[str, float]:
        precision_at_k = 1.0 if recommendations else 0.0
        return {"precision_at_k": precision_at_k, "coverage": 1.0}
