"""Identity resolution service for Customer 360."""
from __future__ import annotations

from typing import Any

from data_quality.repositories.repository import DataQualityRepository


class IdentityResolutionService:
    def __init__(self, repository: DataQualityRepository | None = None):
        self.repository = repository or DataQualityRepository()

    def resolve_identity(self, profile_payload: dict[str, Any]) -> dict[str, Any]:
        candidates = []
        for field in ["email_addresses", "phone_numbers", "external_ids"]:
            values = profile_payload.get(field, [])
            if values:
                candidates.extend(values if isinstance(values, list) else [values])
        return {
            "matched": bool(candidates),
            "confidence": 0.75 if candidates else 0.0,
            "review_required": len(candidates) == 0,
            "matched_fields": [field for field in ["email", "phone", "customer_id"] if field in str(candidates)],
        }
