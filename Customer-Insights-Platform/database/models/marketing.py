"""Marketing automation models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import CampaignChannel, CampaignStatus


class Campaign(TenantModel):
    """Marketing campaign master record."""

    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    channel: Mapped[CampaignChannel] = mapped_column(nullable=False, index=True)
    status: Mapped[CampaignStatus] = mapped_column(default=CampaignStatus.DRAFT, index=True)
    budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))


class Audience(TenantModel):
    """Target audience for campaigns."""

    __tablename__ = "audiences"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    segment_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("segments.id", ondelete="SET NULL"))
    criteria: Mapped[dict] = mapped_column(JSONB, default=dict)
    estimated_size: Mapped[int] = mapped_column(Integer, default=0)


class AudienceMember(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Audience membership."""

    __tablename__ = "audience_members"
    __table_args__ = (UniqueConstraint("audience_id", "customer_id", name="uq_audience_members"),)

    audience_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("audiences.id", ondelete="CASCADE"), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)


class EmailCampaign(TenantModel):
    """Email-specific campaign details."""

    __tablename__ = "email_campaigns"

    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), unique=True, index=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    from_email: Mapped[str] = mapped_column(String(320), nullable=False)
    from_name: Mapped[str] = mapped_column(String(100), nullable=False)
    html_body: Mapped[Optional[str]] = mapped_column(Text)
    text_body: Mapped[Optional[str]] = mapped_column(Text)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class SmsCampaign(TenantModel):
    """SMS campaign details."""

    __tablename__ = "sms_campaigns"

    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), unique=True, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sender_id: Mapped[str] = mapped_column(String(20), nullable=False)


class WhatsappCampaign(TenantModel):
    """WhatsApp campaign details."""

    __tablename__ = "whatsapp_campaigns"

    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), unique=True, index=True)
    template_name: Mapped[str] = mapped_column(String(100), nullable=False)
    template_params: Mapped[dict] = mapped_column(JSONB, default=dict)


class PushCampaign(TenantModel):
    """Push notification campaign details."""

    __tablename__ = "push_campaigns"

    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    deep_link: Mapped[Optional[str]] = mapped_column(String(512))


class CampaignMetric(TenantModel):
    """Aggregated campaign performance metrics."""

    __tablename__ = "campaign_metrics"

    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    sent: Mapped[int] = mapped_column(Integer, default=0)
    delivered: Mapped[int] = mapped_column(Integer, default=0)
    opened: Mapped[int] = mapped_column(Integer, default=0)
    clicked: Mapped[int] = mapped_column(Integer, default=0)
    converted: Mapped[int] = mapped_column(Integer, default=0)
    unsubscribed: Mapped[int] = mapped_column(Integer, default=0)
    revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    ctr: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    conversion_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    roi: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))


class ABTest(TenantModel):
    """A/B test definitions."""

    __tablename__ = "ab_tests"

    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hypothesis: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="running", index=True)
    winner_variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("ab_test_variants.id", ondelete="SET NULL", use_alter=True, name="fk_ab_tests_winner_variant"),
    )
    confidence_level: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))


class ABTestVariant(TenantModel):
    """A/B test variant arms."""

    __tablename__ = "ab_test_variants"

    ab_test_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ab_tests.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_control: Mapped[bool] = mapped_column(Boolean, default=False)
    content: Mapped[dict] = mapped_column(JSONB, default=dict)
    traffic_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=50)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)


class AttributionModel(TenantModel):
    """Marketing attribution model config."""

    __tablename__ = "attribution_models"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)  # first_touch, last_touch, linear, etc.
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class AttributionEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Individual attribution touchpoints."""

    __tablename__ = "attribution_events"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("campaigns.id", ondelete="SET NULL"), index=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    touchpoint_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    revenue_credit: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    conversion_id: Mapped[Optional[uuid.UUID]] = mapped_column(index=True)
