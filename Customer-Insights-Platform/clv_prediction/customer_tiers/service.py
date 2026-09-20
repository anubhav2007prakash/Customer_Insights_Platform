"""Customer value tier assignment service."""
from __future__ import annotations

from typing import Any


class CustomerTierService:
    def assign_tier(self, prediction: dict[str, Any]) -> str:
        clv = float(prediction.get("predicted_clv", 0))
        if clv >= 5000:
            return "Platinum"
        if clv >= 2500:
            return "Gold"
        if clv >= 1000:
            return "Silver"
        if clv >= 500:
            return "Bronze"
        return "Low Value"
