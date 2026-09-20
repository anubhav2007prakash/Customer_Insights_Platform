"""Subscription lifecycle operations: assign, upgrade, downgrade, history."""
from __future__ import annotations

from datetime import datetime
from subscriptions.repositories.sqlalchemy import SubscriptionRepository
from subscriptions.models.subscriptions import Subscription, SubscriptionHistory


class SubscriptionService:
    def __init__(self, repo: SubscriptionRepository | None = None):
        self.repo = repo or SubscriptionRepository()

    def assign_plan(self, organization_id, plan_id, *, starts_at: datetime | None = None, ends_at: datetime | None = None, billing_ref: str | None = None) -> Subscription:
        now = datetime.utcnow()
        sub = Subscription(
            organization_id=organization_id,
            plan_id=plan_id,
            active=True,
            started_at=starts_at or now,
            ends_at=ends_at,
            auto_renew=True,
            billing_reference=billing_ref or "",
        )
        self.repo.set_subscription(sub)
        hist = SubscriptionHistory(
            organization_id=organization_id,
            subscription_id=sub.id,
            action="assign",
            details={"plan_id": str(plan_id)},
        )
        self.repo.session.add(hist)
        self.repo.session.flush()
        return sub

    def change_plan(self, organization_id, new_plan_id, effective_date: datetime | None = None):
        # TODO: implement proration and scheduled changes
        sub = self.repo.get_subscription_for_org(organization_id)
        if not sub:
            return self.assign_plan(organization_id, new_plan_id)
        sub.plan_id = new_plan_id
        self.repo.session.flush()
        hist = SubscriptionHistory(
            organization_id=organization_id,
            subscription_id=sub.id,
            action="change",
            details={"new_plan_id": str(new_plan_id)},
        )
        self.repo.session.add(hist)
        self.repo.session.flush()
        return sub
