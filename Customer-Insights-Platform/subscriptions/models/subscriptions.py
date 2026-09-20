"""Organization subscriptions and history - re-exports canonical model."""
from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

# Re-export canonical Subscription from the shared database models
from database.models.tenant import Subscription  # noqa: F401

from database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class SubscriptionHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "subscription_history"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    subscription_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[dict] = mapped_column(Text, default="{}")

