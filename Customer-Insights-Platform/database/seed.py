"""Reference data seeder for InsightForge AI."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from database.enums import SubscriptionTier
from database.models.tenant import Permission, SubscriptionPlan
from database.models.system import Country, Currency, Language
from database.session import session_scope


def seed_reference_data() -> None:
    """Insert global reference data (idempotent)."""
    with session_scope() as session:
        if not session.scalars(select(Currency).limit(1)).first():
            session.add_all([
                Currency(code="USD", name="US Dollar", symbol="$"),
                Currency(code="EUR", name="Euro", symbol="€"),
                Currency(code="GBP", name="British Pound", symbol="£"),
            ])

        if not session.scalars(select(Country).limit(1)).first():
            session.add_all([
                Country(code="US", name="United States", region="NA"),
                Country(code="GB", name="United Kingdom", region="EMEA"),
                Country(code="IN", name="India", region="APAC"),
            ])

        if not session.scalars(select(Language).limit(1)).first():
            session.add_all([
                Language(code="en-US", name="English (US)"),
                Language(code="en-GB", name="English (UK)"),
            ])

        if not session.scalars(select(SubscriptionPlan).limit(1)).first():
            session.add_all([
                SubscriptionPlan(name="Starter", tier=SubscriptionTier.STARTER, price_monthly=Decimal("99"), max_users=5, max_customers=5000),
                SubscriptionPlan(name="Professional", tier=SubscriptionTier.PROFESSIONAL, price_monthly=Decimal("499"), max_users=25, max_customers=50000),
                SubscriptionPlan(name="Enterprise", tier=SubscriptionTier.ENTERPRISE, price_monthly=Decimal("2499"), max_users=100, max_customers=1000000),
            ])

        if not session.scalars(select(Permission).limit(1)).first():
            modules = [
                ("customers.read", "customers"), ("customers.write", "customers"),
                ("analytics.read", "analytics"), ("reports.read", "reports"),
                ("reports.write", "reports"), ("admin.users", "admin"),
                ("ai.query", "ai"), ("integrations.manage", "integrations"),
            ]
            session.add_all([Permission(code=code, module=mod) for code, mod in modules])


if __name__ == "__main__":
    seed_reference_data()
    print("Reference data seeded.")
