"""SQLAlchemy repositories for subscription and entitlement data."""
from __future__ import annotations

from typing import Optional
from sqlalchemy import select
from database.session import SessionLocal
from subscriptions.models.plans import Plan
from subscriptions.models.subscriptions import Subscription
from subscriptions.models.entitlements import Feature, Entitlement, ModuleLicense


class SubscriptionRepository:
    def __init__(self, session=None):
        self.session = session or SessionLocal()
        self._own = session is None

    def get_plan_by_slug(self, slug: str) -> Optional[Plan]:
        return self.session.scalars(select(Plan).where(Plan.slug == slug)).first()

    def add_plan(self, plan: Plan) -> Plan:
        self.session.add(plan)
        self.session.flush()
        return plan

    def get_subscription_for_org(self, organization_id):
        return self.session.scalars(select(Subscription).where(Subscription.organization_id == organization_id)).first()

    def set_subscription(self, subscription: Subscription) -> Subscription:
        self.session.add(subscription)
        self.session.flush()
        return subscription

    def get_feature_by_key(self, key: str) -> Optional[Feature]:
        return self.session.scalars(select(Feature).where(Feature.key == key)).first()

    def get_entitlement(self, organization_id, feature_id) -> Optional[Entitlement]:
        return self.session.scalars(select(Entitlement).where(Entitlement.organization_id == organization_id, Entitlement.feature_id == feature_id)).first()

    def get_module_license(self, organization_id, module_key) -> Optional[ModuleLicense]:
        return self.session.scalars(select(ModuleLicense).where(ModuleLicense.organization_id == organization_id, ModuleLicense.module_key == module_key)).first()

    def close(self):
        if self._own:
            self.session.close()
