"""Core service for creating and managing customer profiles."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from customer360.profiles.models import CustomerProfile
from data_quality.repositories.repository import DataQualityRepository


class CustomerProfileService:
    def __init__(self, repository: DataQualityRepository | None = None):
        self.repository = repository or DataQualityRepository()

    def create_profile(self, organization_id, payload: dict[str, Any]) -> CustomerProfile:
        profile = CustomerProfile(
            organization_id=organization_id,
            external_ids=payload.get("external_ids", {}),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            full_name=payload.get("full_name") or self._build_full_name(payload),
            preferred_name=payload.get("preferred_name"),
            gender=payload.get("gender"),
            date_of_birth=payload.get("date_of_birth"),
            email_addresses=payload.get("email_addresses", []),
            phone_numbers=payload.get("phone_numbers", []),
            addresses=payload.get("addresses", []),
            country=payload.get("country"),
            state=payload.get("state"),
            city=payload.get("city"),
            postal_code=payload.get("postal_code"),
            time_zone=payload.get("time_zone"),
            language=payload.get("language"),
            company=payload.get("company"),
            job_title=payload.get("job_title"),
            industry=payload.get("industry"),
            source_system=payload.get("source_system"),
            last_activity=payload.get("last_activity"),
            profile_completion_pct=self._completion_pct(payload),
            profile_status=payload.get("profile_status", "active"),
            customer_type=payload.get("customer_type", "B2C"),
            custom_attributes=payload.get("custom_attributes", {}),
            notes=payload.get("notes"),
        )
        return self.repository.add_profile(profile)

    def get_profile(self, profile_id) -> CustomerProfile | None:
        return self.repository.session.get(CustomerProfile, profile_id)

    def update_profile(self, profile: CustomerProfile, payload: dict[str, Any]) -> CustomerProfile:
        for key, value in payload.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.updated_at = datetime.utcnow()
        profile.profile_completion_pct = self._completion_pct({k: getattr(profile, k) for k in payload})
        self.repository.session.flush()
        return profile

    def _build_full_name(self, payload: dict[str, Any]) -> str:
        first = payload.get("first_name") or ""
        last = payload.get("last_name") or ""
        return f"{first} {last}".strip()

    def _completion_pct(self, payload: dict[str, Any]) -> int:
        fields = ["first_name", "last_name", "email_addresses", "phone_numbers", "country", "city"]
        filled = sum(1 for field in fields if payload.get(field))
        return int((filled / len(fields)) * 100)
