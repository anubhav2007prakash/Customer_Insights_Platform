"""Initial schema: PostgreSQL extensions + full InsightForge AI schema.

Revision ID: 001
Revises:
Create Date: 2026-07-02

Migration plan
--------------
001  Extensions (uuid-ossp, pgvector) + full schema via metadata
002  Seed reference data (currencies, countries, permissions, plans)
003  Materialized views for analytics (mv_daily_revenue, mv_customer_kpis)
004  Partitioning for high-volume tables (page_views, customer_events, audit_logs)
005  Row-level security policies for multi-tenant isolation
006  Additional indexes from production query analysis
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from database.base import Base
import database.models  # noqa: F401

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create all tables from SQLAlchemy metadata
    bind = op.get_bind()
    Base.metadata.create_all(bind)

    # Composite indexes for high-traffic query patterns
    op.create_index(
        "ix_customers_org_status_stage",
        "customers",
        ["organization_id", "status", "lifecycle_stage"],
        unique=False,
    )
    op.create_index(
        "ix_orders_org_placed_at",
        "orders",
        ["organization_id", "placed_at"],
        unique=False,
    )
    op.create_index(
        "ix_customer_events_org_occurred",
        "customer_events",
        ["organization_id", "occurred_at"],
        unique=False,
    )
    op.create_index(
        "ix_page_views_org_viewed",
        "page_views",
        ["organization_id", "viewed_at"],
        unique=False,
    )
    op.create_index(
        "ix_audit_logs_org_created",
        "audit_logs",
        ["organization_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_kpi_snapshots_org_category_period",
        "kpi_snapshots",
        ["organization_id", "category", "period_start"],
        unique=False,
    )

    # Partial index for active (non-deleted) records
    op.execute("""
        CREATE INDEX ix_customers_active
        ON customers (organization_id, email)
        WHERE deleted_at IS NULL
    """)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind)
    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
