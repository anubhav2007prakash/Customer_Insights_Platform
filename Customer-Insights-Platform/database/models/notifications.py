"""Notification system models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import NotificationChannel, NotificationPriority


class Notification(TenantModel):
    """In-app and multi-channel notifications."""

    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(default=NotificationChannel.IN_APP, index=True)
    priority: Mapped[NotificationPriority] = mapped_column(default=NotificationPriority.NORMAL, index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    action_url: Mapped[Optional[str]] = mapped_column(String(512))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class NotificationChannelConfig(TenantModel):
    """Organization notification channel configuration."""

    __tablename__ = "notification_channels"

    channel: Mapped[NotificationChannel] = mapped_column(nullable=False, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict] = mapped_column(JSONB, default=dict)


class NotificationTemplate(TenantModel):
    """Notification message templates."""

    __tablename__ = "notification_templates"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject_template: Mapped[Optional[str]] = mapped_column(String(255))
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class NotificationDeliveryLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Delivery attempt logs."""

    __tablename__ = "notification_delivery_logs"

    notification_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notifications.id", ondelete="CASCADE"), index=True)
    channel: Mapped[NotificationChannel] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(128))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
