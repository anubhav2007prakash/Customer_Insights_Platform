"""Summary generation service for segmentation insights."""
from __future__ import annotations

from typing import Any


class SummaryService:
    def summarize(self, profile: dict[str, Any], name: str, monitoring: dict[str, Any]) -> dict[str, Any]:
        return {
            "segment_name": name,
            "customer_count": profile.get("customer_count", 0),
            "average_revenue": profile.get("average_revenue", 0),
            "monitoring_status": monitoring.get("status", "unknown"),
            "summary": f"{name} segment contains {profile.get('customer_count', 0)} customers.",
        }

    def generate(self, customers: list[dict[str, Any]], segment_name: str) -> str:
        revenue = sum(customer.get("total_revenue", 0) for customer in customers)
        return f"{segment_name} segment summarizes {len(customers)} customers and {revenue} revenue."


SegmentationSummaryService = SummaryService
