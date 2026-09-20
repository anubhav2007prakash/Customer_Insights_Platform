"""Sales intelligence models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import DealStage, LeadStatus


class LeadSource(TenantModel):
    """Lead source catalog."""

    __tablename__ = "lead_sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Lead(TenantModel):
    """Sales leads."""

    __tablename__ = "leads"

    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("lead_sources.id", ondelete="SET NULL"))
    status: Mapped[LeadStatus] = mapped_column(default=LeadStatus.NEW, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    email: Mapped[Optional[str]] = mapped_column(String(320), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32))
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    estimated_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class LeadScore(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Lead scoring history."""

    __tablename__ = "lead_scores"

    lead_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    factors: Mapped[dict] = mapped_column(JSONB, default=dict)
    model_version: Mapped[Optional[str]] = mapped_column(String(50))
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class PipelineStage(TenantModel):
    """Configurable pipeline stages."""

    __tablename__ = "pipeline_stages"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    probability: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    is_won: Mapped[bool] = mapped_column(Boolean, default=False)
    is_lost: Mapped[bool] = mapped_column(Boolean, default=False)


class Deal(TenantModel):
    """Sales opportunities / deals."""

    __tablename__ = "deals"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("leads.id", ondelete="SET NULL"))
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    stage: Mapped[DealStage] = mapped_column(default=DealStage.PROSPECTING, index=True)
    pipeline_stage_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("pipeline_stages.id", ondelete="SET NULL"))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    probability: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    expected_close_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    lost_reason: Mapped[Optional[str]] = mapped_column(String(255))


class SalesActivity(TenantModel):
    """Sales rep activities (calls, emails, demos)."""

    __tablename__ = "sales_activities"

    deal_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("deals.id", ondelete="CASCADE"), index=True)
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)


class SalesTask(TenantModel):
    """Sales follow-up tasks."""

    __tablename__ = "sales_tasks"

    deal_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("deals.id", ondelete="CASCADE"), index=True)
    assigned_to_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    priority: Mapped[str] = mapped_column(String(20), default="medium")


class Meeting(TenantModel):
    """Scheduled sales meetings."""

    __tablename__ = "meetings"

    deal_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("deals.id", ondelete="SET NULL"), index=True)
    organizer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    meeting_url: Mapped[Optional[str]] = mapped_column(String(512))
    attendees: Mapped[list] = mapped_column(JSONB, default=list)


class SalesForecast(TenantModel):
    """Revenue forecast snapshots."""

    __tablename__ = "sales_forecasts"

    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    forecast_amount: Mapped[Decimal] = mapped_column(Numeric(16, 2), nullable=False)
    committed_amount: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0)
    best_case_amount: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0)
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
