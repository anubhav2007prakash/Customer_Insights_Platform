"""Apply validation rules to dataset rows."""
from __future__ import annotations

from typing import Iterable
from data_quality.rules.registry import rule_registry
from data_quality.rules.core import DataQualityRule


class ValidationRuleEngine:
    def __init__(self, rules: Iterable[DataQualityRule] | None = None):
        self.rules = list(rules or [])

    def apply(self, rows: Iterable[dict]) -> list[dict]:
        results: list[dict] = []

        for idx, row in enumerate(rows):
            row_results = {"row_index": idx, "validations": []}
            for rule in self.rules:
                row_results["validations"].append({
                    "rule": rule.name,
                    **rule.validate(row),
                })
            results.append(row_results)

        return results

    @classmethod
    def from_config(cls, config: list[dict]) -> ValidationRuleEngine:
        rules: list[DataQualityRule] = []
        for rule_config in config:
            rule_cls = rule_registry.get(rule_config.get("name"))
            if not rule_cls:
                continue
            params = rule_config.get("params", {})
            rules.append(rule_cls(**params))
        return cls(rules)
