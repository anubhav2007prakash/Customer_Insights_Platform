"""RFM segmentation utilities."""
from __future__ import annotations

from typing import Any


class RFMService:
    def calculate(self, records: list[dict[str, Any]], thresholds: dict[str, int] | None = None) -> list[dict[str, Any]]:
        thresholds = thresholds or {"recency": 90, "frequency": 3, "monetary": 100}
        outputs = []
        for record in records:
            recency = int(record.get("recency", 0))
            frequency = int(record.get("frequency", 0))
            monetary = float(record.get("monetary", 0))
            segment = "cold"
            if recency <= thresholds["recency"] and frequency >= thresholds["frequency"] and monetary >= thresholds["monetary"]:
                segment = "champion"
            elif recency <= thresholds["recency"] and frequency >= thresholds["frequency"]:
                segment = "loyal"
            elif frequency >= thresholds["frequency"]:
                segment = "active"
            outputs.append(
                {
                    "customer_id": record.get("customer_id"),
                    "segment": segment,
                    "recency": recency,
                    "frequency": frequency,
                    "monetary": monetary,
                }
            )
        return outputs
