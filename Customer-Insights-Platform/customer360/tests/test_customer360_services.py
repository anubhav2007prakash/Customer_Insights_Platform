from __future__ import annotations

import uuid

from customer360.identity.service import IdentityResolutionService
from customer360.lifecycle.service import LifecycleService
from customer360.profiles.models import CustomerProfile
from customer360.scoring.service import ScoringService
from customer360.services.profile_service import CustomerProfileService
from customer360.timeline.service import TimelineService


def test_profile_creation_and_completion():
    service = CustomerProfileService()
    profile = service.create_profile(
        organization_id=uuid.uuid4(),
        payload={
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email_addresses": ["ada@example.com"],
            "phone_numbers": ["+1-555-0100"],
            "country": "US",
            "city": "London",
        },
    )
    assert profile.full_name == "Ada Lovelace"
    assert profile.profile_completion_pct >= 50


def test_identity_resolution_service():
    service = IdentityResolutionService()
    result = service.resolve_identity({"email_addresses": ["ada@example.com"], "external_ids": {"crm_id": "123"}})
    assert result["matched"] is True
    assert result["confidence"] >= 0.5


def test_timeline_generation():
    service = TimelineService()
    events = [{"event_type": "purchase", "event_time": "2024-01-01T00:00:00"}]
    timeline = service.build_timeline(profile_id=uuid.uuid4(), events=events)
    assert timeline[0]["event_type"] == "purchase"


def test_lifecycle_service():
    service = LifecycleService()
    profile = CustomerProfile(organization_id=uuid.uuid4(), profile_status="active")
    assert service.get_stage(profile) == "active"
    assert service.update_stage(profile, "vip_customer") == "vip_customer"


def test_scoring_service():
    service = ScoringService()
    profile = CustomerProfile(organization_id=uuid.uuid4(), profile_completion_pct=80)
    scores = service.calculate_scores(profile)
    assert scores["health_score"] == 80.0
    assert scores["churn_risk_score"] == 20.0
