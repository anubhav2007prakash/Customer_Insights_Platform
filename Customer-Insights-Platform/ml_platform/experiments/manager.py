"""Experiment tracking for training runs."""
from __future__ import annotations

from typing import Any


class ExperimentTracker:
    def __init__(self) -> None:
        self._experiments: list[dict[str, Any]] = []

    def create_experiment(self, name: str, params: dict[str, Any], dataset_version: str | None = None, notes: str | None = None) -> dict[str, Any]:
        experiment = {
            "name": name,
            "params": params,
            "dataset_version": dataset_version,
            "notes": notes,
        }
        self._experiments.append(experiment)
        return experiment

    def list_experiments(self) -> list[dict[str, Any]]:
        return list(self._experiments)
