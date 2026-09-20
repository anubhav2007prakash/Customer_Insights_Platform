"""Core abstraction for data quality rules."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DataQualityRule(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate(self, row: dict) -> dict:
        raise NotImplementedError

    def supports_dataset(self, dataset_name: str) -> bool:
        return True
