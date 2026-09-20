"""Dataset management for the ML platform."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Dataset:
    name: str
    version: str
    metadata: dict[str, Any]
    rows: list[dict[str, Any]] = field(default_factory=list)
    dataset_id: str = ""


class DatasetManager:
    def __init__(self) -> None:
        self._datasets: list[Dataset] = []

    def register_dataset(self, name: str, version: str, metadata: dict[str, Any], rows: list[dict[str, Any]]) -> Dataset:
        dataset = Dataset(name=name, version=version, metadata=metadata, rows=rows, dataset_id=f"{name}:{version}")
        self._datasets.append(dataset)
        return dataset

    def get_dataset(self, dataset_id: str) -> Dataset | None:
        return next((dataset for dataset in self._datasets if dataset.dataset_id == dataset_id), None)

    def train_test_split(self, dataset: Dataset, test_size: float = 0.2) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        split_index = max(1, int(len(dataset.rows) * (1 - test_size)))
        train_rows = dataset.rows[:split_index]
        test_rows = dataset.rows[split_index:]
        return train_rows, test_rows

    def validate_dataset(self, dataset: Dataset) -> dict[str, Any]:
        return {"dataset_id": dataset.dataset_id, "row_count": len(dataset.rows), "valid": len(dataset.rows) > 0}
