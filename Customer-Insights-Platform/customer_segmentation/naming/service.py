"""Segment naming service."""
from __future__ import annotations

from typing import Any


class SegmentNamingService:
    def name(self, profile: dict[str, Any]) -> str:
        if profile.get("average_revenue", 0) > 200:
            return "High Value"
        if profile.get("average_engagement_score", 0) > 2:
            return "Engaged"
        return "Standard"

    def generate_name(self, value_tier: str, loyalty_tier: str) -> str:
        if value_tier.lower() == "high" and loyalty_tier.lower() == "loyal":
            return "High Growth Customers"
        return "Standard Customers"
