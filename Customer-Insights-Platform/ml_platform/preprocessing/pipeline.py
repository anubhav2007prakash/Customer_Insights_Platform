"""Reusable preprocessing pipeline for tabular data."""
from __future__ import annotations

from typing import Any


class PreprocessingPipeline:
    def __init__(self) -> None:
        self._fill_value: float = 0.0

    def fit_transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        transformed: list[dict[str, Any]] = []
        for row in rows:
            normalized = dict(row)
            for key, value in normalized.items():
                if value is None:
                    normalized[key] = self._fill_value
                elif isinstance(value, (int, float)) and key != "label":
                    normalized[key] = float(value)
            transformed.append(normalized)
        return transformed
