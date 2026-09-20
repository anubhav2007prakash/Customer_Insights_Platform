"""Registry for configurable data quality validation rules."""
from __future__ import annotations

from typing import Dict, Type

from data_quality.rules.core import DataQualityRule


class RuleRegistry:
    def __init__(self):
        self._rules: Dict[str, Type[DataQualityRule]] = {}

    def register(self, rule: Type[DataQualityRule]) -> None:
        self._rules[rule.__name__] = rule

    def get(self, name: str) -> Type[DataQualityRule] | None:
        return self._rules.get(name)

    def available(self) -> list[str]:
        return list(self._rules.keys())


rule_registry = RuleRegistry()
