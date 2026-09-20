"""Policy-related DB models (lightweight) for audit and policy metadata."""
from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantModel


class Policy(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "policies"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)


class PolicyRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "policy_rules"

    policy_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("policies.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    expression: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class PolicyAuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "policy_audit_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource: Mapped[str] = mapped_column(String(200))
    allowed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason: Mapped[str] = mapped_column(String(200))


class DataClassification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "data_classifications"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text)


class FieldPermission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "field_permissions"

    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    permission_code: Mapped[str] = mapped_column(String(100), nullable=False)


class MaskingRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "masking_rules"

    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    params: Mapped[str] = mapped_column(Text, default="{}")
