"""Customer 360 data models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import CustomerStatus, LeadStatus, LifecycleStage, ScoreType


class Customer(TenantModel):
    """Core customer record — anchor for Customer 360."""

    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("organization_id", "external_id", name="uq_customers_org_external"),)

    external_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    email: Mapped[Optional[str]] = mapped_column(String(320), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32))
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    full_name: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    status: Mapped[CustomerStatus] = mapped_column(default=CustomerStatus.PROSPECT, index=True)
    lead_status: Mapped[Optional[LeadStatus]] = mapped_column(index=True)
    lifecycle_stage: Mapped[LifecycleStage] = mapped_column(default=LifecycleStage.LEAD, index=True)
    source: Mapped[Optional[str]] = mapped_column(String(100))
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    business: Mapped[Optional["CustomerBusinessDetail"]] = relationship(back_populates="customer", uselist=False)
    scores: Mapped[list["CustomerScore"]] = relationship(back_populates="customer")
    notes: Mapped[list["CustomerNote"]] = relationship(back_populates="customer")


class CustomerBusinessDetail(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """B2B business attributes."""

    __tablename__ = "customer_business_details"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), unique=True, index=True,
    )
    company_name: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    company_size: Mapped[Optional[str]] = mapped_column(String(50))
    annual_revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2))
    website: Mapped[Optional[str]] = mapped_column(String(512))
    tax_id: Mapped[Optional[str]] = mapped_column(String(50))

    customer: Mapped["Customer"] = relationship(back_populates="business")


class CustomerAddress(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Customer physical addresses."""

    __tablename__ = "customer_addresses"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(50), default="primary")
    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)


class CustomerCommunication(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Communication preferences and channels."""

    __tablename__ = "customer_communications"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(30), nullable=False)
    value: Mapped[str] = mapped_column(String(320), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    opted_in: Mapped[bool] = mapped_column(Boolean, default=True)


class CustomerSocialProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Social media profiles."""

    __tablename__ = "customer_social_profiles"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    profile_url: Mapped[str] = mapped_column(String(512), nullable=False)
    handle: Mapped[Optional[str]] = mapped_column(String(100))


class Tag(TenantModel):
    """Reusable tag definitions."""

    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_tags_org_name"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(7))


class CustomerTag(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Customer ↔ tag association."""

    __tablename__ = "customer_tags"
    __table_args__ = (UniqueConstraint("customer_id", "tag_id", name="uq_customer_tags"),)

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), index=True)


class Segment(TenantModel):
    """Dynamic or static customer segments."""

    __tablename__ = "segments"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    criteria: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_dynamic: Mapped[bool] = mapped_column(Boolean, default=True)
    member_count: Mapped[int] = mapped_column(Integer, default=0)


class CustomerSegmentMember(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Segment membership."""

    __tablename__ = "customer_segment_members"
    __table_args__ = (UniqueConstraint("segment_id", "customer_id", name="uq_segment_members"),)

    segment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("segments.id", ondelete="CASCADE"), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CustomerScore(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Computed scores: health, engagement, CLV, churn, etc."""

    __tablename__ = "customer_scores"
    __table_args__ = (UniqueConstraint("customer_id", "score_type", name="uq_customer_scores"),)

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    score_type: Mapped[ScoreType] = mapped_column(nullable=False, index=True)
    value: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    previous_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    model_version: Mapped[Optional[str]] = mapped_column(String(50))
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    customer: Mapped["Customer"] = relationship(back_populates="scores")


class CustomerNote(TenantModel):
    """Internal notes on customers."""

    __tablename__ = "customer_notes"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)

    customer: Mapped["Customer"] = relationship(back_populates="notes")


class CustomerAttachment(TenantModel):
    """Files attached to customer records."""

    __tablename__ = "customer_attachments"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("file_uploads.id", ondelete="CASCADE"))
    description: Mapped[Optional[str]] = mapped_column(String(255))


class CustomerAISummary(TenantModel):
    """AI-generated customer summaries."""

    __tablename__ = "customer_ai_summaries"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CustomerLifecycleEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Lifecycle stage transition events."""

    __tablename__ = "customer_lifecycle_events"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    from_stage: Mapped[Optional[LifecycleStage]] = mapped_column()
    to_stage: Mapped[LifecycleStage] = mapped_column(nullable=False)
    triggered_by: Mapped[Optional[str]] = mapped_column(String(100))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
