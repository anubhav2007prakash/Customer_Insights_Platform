"""SQLAlchemy declarative base and shared mixins."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, MetaData, Uuid, func, JSON, String
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB, INET as PG_INET
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

# Cross-dialect JSONB & INET: PG types on PostgreSQL, standard types on SQLite
JSONB = JSON().with_variant(PG_JSONB, "postgresql")
INET = String(45).with_variant(PG_INET, "postgresql")

# Consistent naming for Alembic autogenerate
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Root declarative base for all InsightForge AI models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class UUIDPrimaryKeyMixin:
    """UUID v4 primary key mixin."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    """Automatic created_at / updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Soft-delete support via deleted_at."""

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class TenantMixin:
    """Multi-tenant organization scope — required on all business records."""

    @declared_attr
    def organization_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            Uuid(as_uuid=True),
            ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )


class WorkspaceScopedMixin(TenantMixin):
    """Optional workspace scope within an organization."""

    @declared_attr
    def workspace_id(cls) -> Mapped[Optional[uuid.UUID]]:
        return mapped_column(
            Uuid(as_uuid=True),
            ForeignKey("workspaces.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )


class BaseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Abstract base with UUID PK, timestamps, and soft delete."""

    __abstract__ = True


class TenantModel(BaseModel, TenantMixin):
    """Abstract tenant-scoped business entity."""

    __abstract__ = True


class WorkspaceModel(TenantModel, WorkspaceScopedMixin):
    """Abstract workspace-scoped entity."""

    __abstract__ = True
