"""System and reference data models."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, BaseModel, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import FeatureFlagScope


class AppSetting(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Global application settings."""

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)


class OrganizationSetting(TenantModel):
    """Per-organization settings."""

    __tablename__ = "organization_settings"

    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        {"comment": "Key-value settings scoped to organization"},
    )


class Currency(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ISO currency reference."""

    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    decimal_places: Mapped[int] = mapped_column(default=2)


class Country(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ISO country reference."""

    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[Optional[str]] = mapped_column(String(50))


class Language(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Supported languages."""

    __tablename__ = "languages"

    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_rtl: Mapped[bool] = mapped_column(Boolean, default=False)


class Theme(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """UI theme definitions."""

    __tablename__ = "themes"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    tokens: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class SystemLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Application system logs."""

    __tablename__ = "system_logs"

    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    module: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), index=True,
    )
