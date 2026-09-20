"""Customer profile models for the Customer 360 engine."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from database.base import TenantModel


class CustomerProfile(TenantModel):
    __tablename__ = "customer_profiles"

    external_ids: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    preferred_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    email_addresses: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    phone_numbers: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    addresses: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    time_zone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_activity: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    profile_completion_pct: Mapped[int] = mapped_column(default=0, nullable=False)
    profile_status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    customer_type: Mapped[str] = mapped_column(String(20), nullable=False, default="B2C")
    custom_attributes: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
