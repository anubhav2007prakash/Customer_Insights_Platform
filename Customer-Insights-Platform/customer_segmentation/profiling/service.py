"""Segment profiling service."""
from __future__ import annotations

from typing import Any


class SegmentProfilingService:
    def build_profile(self, customers: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "customer_count": len(customers),
            "average_revenue": sum(customer.get("total_revenue", 0) for customer in customers) / max(1, len(customers)),
            "average_lifetime": sum(customer.get("customer_lifetime", 0) for customer in customers) / max(1, len(customers)),
            "average_health_score": sum(customer.get("health_score", 0) for customer in customers) / max(1, len(customers)),
            "average_loyalty_score": sum(customer.get("loyalty_score", 0) for customer in customers) / max(1, len(customers)),
            "average_engagement_score": sum(customer.get("engagement_score", 0) for customer in customers) / max(1, len(customers)),
        }
