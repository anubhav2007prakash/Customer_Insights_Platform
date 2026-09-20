"""Customer behavior and web analytics models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB, INET


class WebSession(TenantModel):
    """Website visit sessions."""

    __tablename__ = "web_sessions"

    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    session_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    page_views: Mapped[int] = mapped_column(Integer, default=0)
    bounced: Mapped[bool] = mapped_column(Boolean, default=False)
    device_type: Mapped[Optional[str]] = mapped_column(String(30))
    browser: Mapped[Optional[str]] = mapped_column(String(50))
    os: Mapped[Optional[str]] = mapped_column(String(50))
    ip_address: Mapped[Optional[str]] = mapped_column(INET)
    country_code: Mapped[Optional[str]] = mapped_column(String(2), index=True)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    referrer: Mapped[Optional[str]] = mapped_column(String(512))
    utm_source: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    utm_medium: Mapped[Optional[str]] = mapped_column(String(100))
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(100), index=True)


class PageView(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Individual page view events."""

    __tablename__ = "page_views"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("web_sessions.id", ondelete="CASCADE"), index=True)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    path: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    viewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    time_on_page_seconds: Mapped[Optional[int]] = mapped_column(Integer)


class ClickEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Click tracking events."""

    __tablename__ = "click_events"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("web_sessions.id", ondelete="CASCADE"), index=True)
    element_id: Mapped[Optional[str]] = mapped_column(String(255))
    element_text: Mapped[Optional[str]] = mapped_column(String(255))
    page_path: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    coordinates: Mapped[dict] = mapped_column(JSONB, default=dict)


class ScrollEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Scroll depth tracking."""

    __tablename__ = "scroll_events"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("web_sessions.id", ondelete="CASCADE"), index=True)
    page_path: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    max_depth_percent: Mapped[int] = mapped_column(Integer, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SearchEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """On-site search history."""

    __tablename__ = "search_events"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("web_sessions.id", ondelete="SET NULL"), index=True)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    query: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    searched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class CustomerEvent(TenantModel):
    """Generic customer behavior events."""

    __tablename__ = "customer_events"

    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("web_sessions.id", ondelete="SET NULL"))
    event_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_category: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    properties: Mapped[dict] = mapped_column(JSONB, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class Funnel(TenantModel):
    """Conversion funnel definitions."""

    __tablename__ = "funnels"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class FunnelStep(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Steps within a funnel."""

    __tablename__ = "funnel_steps"

    funnel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("funnels.id", ondelete="CASCADE"), index=True)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_name: Mapped[str] = mapped_column(String(100), nullable=False)


class CustomerJourney(TenantModel):
    """End-to-end customer journey instances."""

    __tablename__ = "customer_journeys"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)


class JourneyTouchpoint(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Touchpoints along a customer journey."""

    __tablename__ = "journey_touchpoints"

    journey_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customer_journeys.id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
