"""Subscription plan models."""
from __future__ import annotations

import uuid
from sqlalchemy import String, Text, Numeric, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class Plan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "plans"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    monthly_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    annual_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(String(20), default="active")
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    trial_available: Mapped[bool] = mapped_column(Boolean, default=False)
    default_plan: Mapped[bool] = mapped_column(Boolean, default=False)
    max_users: Mapped[int] = mapped_column(Integer, default=5)
    max_storage_gb: Mapped[int] = mapped_column(Integer, default=10)
    max_api_calls_per_month: Mapped[int] = mapped_column(Integer, default=10000)

    versions: Mapped[list["PlanVersion"]] = relationship(back_populates="plan")


class PlanVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "plan_versions"

    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"), index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[dict] = mapped_column(Text, default="{}")

    plan: Mapped["Plan"] = relationship(back_populates="versions")
