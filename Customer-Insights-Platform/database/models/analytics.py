"""Analytics, KPI, and aggregation models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import KPICategory


class KPISnapshot(TenantModel):
    """Point-in-time KPI values (denormalized for BI)."""

    __tablename__ = "kpi_snapshots"

    category: Mapped[KPICategory] = mapped_column(nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[Decimal] = mapped_column(Numeric(16, 4), nullable=False)
    previous_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 4))
    change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    granularity: Mapped[str] = mapped_column(String(20), default="daily")  # hourly|daily|weekly|monthly
    dimensions: Mapped[dict] = mapped_column(JSONB, default=dict)


class DashboardCache(TenantModel):
    """Pre-computed dashboard widget data."""

    __tablename__ = "dashboard_cache"

    dashboard_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    widget_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AnalyticsAggregation(TenantModel):
    """Roll-up aggregations for analytics queries."""

    __tablename__ = "analytics_aggregations"

    aggregation_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    dimensions: Mapped[dict] = mapped_column(JSONB, default=dict)
    metrics: Mapped[dict] = mapped_column(JSONB, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    grain: Mapped[str] = mapped_column(String(20), nullable=False)


class AnalyticsSnapshot(TenantModel):
    """Periodic analytics snapshots for trend analysis."""

    __tablename__ = "analytics_snapshots"

    snapshot_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, default=0)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class MaterializedViewRefreshLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks materialized view refresh jobs."""

    __tablename__ = "materialized_view_refresh_log"

    view_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    row_count: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
