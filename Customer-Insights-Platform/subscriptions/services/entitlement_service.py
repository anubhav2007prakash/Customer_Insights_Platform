"""Entitlement service centralizing feature/plan checks."""
from __future__ import annotations

from typing import Optional
from subscriptions.repositories.sqlalchemy import SubscriptionRepository


class EntitlementService:
    def __init__(self, repo: SubscriptionRepository | None = None):
        self.repo = repo or SubscriptionRepository()

    def has_feature(self, organization_id, feature_key: str) -> bool:
        feat = self.repo.get_feature_by_key(feature_key)
        if not feat:
            return False
        ent = self.repo.get_entitlement(organization_id, feat.id)
        if ent is None:
            return bool(feat.default_enabled)
        return bool(ent.enabled)

    def can_use_ai(self, organization_id) -> bool:
        # Example: AI pack must be licensed or plan includes AI
        ml = self.repo.get_module_license(organization_id, "ai_pack")
        return bool(ml and ml.enabled)

    def remaining_ai_credits(self, organization_id) -> int:
        # Placeholder: connect to usage store
        return 0

    def remaining_storage_gb(self, organization_id) -> int:
        # Placeholder: inspect usage and plan limits
        return 0

    def remaining_users(self, organization_id) -> int:
        # Placeholder: inspect subscription and count users
        return -1
