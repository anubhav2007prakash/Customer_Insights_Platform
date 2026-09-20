"""Built-in uniqueness validation rule."""
from __future__ import annotations

from data_quality.rules.core import DataQualityRule


class UniqueFieldRule(DataQualityRule):
    def __init__(self, field_name: str):
        self.field_name = field_name

    @property
    def name(self) -> str:
        return "UniqueFieldRule"

    def validate(self, row: dict) -> dict:
        value = row.get(self.field_name)
        if value is None:
            return {"passed": False, "reason": f"{self.field_name} is missing.", "value": value}

        return {"passed": True, "reason": None, "value": value}
