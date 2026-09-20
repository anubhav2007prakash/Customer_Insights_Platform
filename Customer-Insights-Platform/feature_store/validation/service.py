"""Feature validation service."""
from __future__ import annotations

from typing import Any


class FeatureValidationService:
    def validate(self, feature: dict[str, Any]) -> dict[str, Any]:
        approved = True
        reasons = []
        if feature.get("null_percentage", 0) > 0.5:
            approved = False
            reasons.append("null_percentage too high")
        if feature.get("cardinality", 0) <= 1:
            approved = False
            reasons.append("cardinality too low")
        return {"approved": approved, "reasons": reasons}
