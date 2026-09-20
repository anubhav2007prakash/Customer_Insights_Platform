"""Dataset preparation for forecasting workflows."""
from __future__ import annotations

from typing import Any


class ForecastDatasetService:
    def prepare_dataset(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "series_id": f"{record.get('product', 'unknown')}:{record.get('region', 'unknown')}",
                "date": record.get("date"),
                "value": float(record.get("value", 0.0)),
                "product": record.get("product", "unknown"),
                "region": record.get("region", "unknown"),
            }
            for record in records
        ]
