"""Feature and module entitlement models."""
from __future__ import annotations

import uuid
from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class Feature(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "features"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    default_enabled: Mapped[bool] = mapped_column(Boolean, default=False)


class ModuleLicense(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "module_licenses"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    module_key: Mapped[str] = mapped_column(String(100), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_: Mapped[dict] = mapped_column("metadata", Text, default="{}")


class Entitlement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "entitlements"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    feature_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("features.id", ondelete="CASCADE"), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    config: Mapped[dict] = mapped_column(Text, default="{}")
