"""Training service for churn models."""
from __future__ import annotations

from typing import Any

from ml_platform.training.trainer import ModelTrainer


class ChurnTrainingService:
    def __init__(self, trainer: ModelTrainer | None = None) -> None:
        self.trainer = trainer or ModelTrainer()

    def train(self, customers: list[dict[str, Any]]) -> dict[str, Any]:
        rows = [
            {"customer_id": customer.get("customer_id"), "target": customer.get("churn_label", 0)}
            for customer in customers
        ]
        model = self.trainer.train(rows, task_type="classification")
        return {
            **model,
            "algorithm": "random_forest",
            "version": "v1",
            "trained_customers": len(customers),
        }
