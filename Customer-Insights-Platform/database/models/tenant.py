"""Multi-tenant organization models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import BaseModel, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base, JSONB
from database.enums import (
    FeatureFlagScope, InvitationStatus, OrganizationStatus, SubscriptionStatus, SubscriptionTier,
)


class Organization(BaseModel):
    """Top-level SaaS tenant — all business data is scoped here."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[OrganizationStatus] = mapped_column(default=OrganizationStatus.TRIAL, index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    company_size: Mapped[Optional[str]] = mapped_column(String(50))
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    locale: Mapped[str] = mapped_column(String(16), default="en-US")
    logo_url: Mapped[Optional[str]] = mapped_column(String(512))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    workspaces: Mapped[list["Workspace"]] = relationship(back_populates="organization")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="organization")
    billing_accounts: Mapped[list["BillingAccount"]] = relationship(back_populates="organization")


class Workspace(TenantModel):
    """Logical partition within an organization (prod/staging/team)."""

    __tablename__ = "workspaces"
    __table_args__ = (UniqueConstraint("organization_id", "slug", name="uq_workspaces_org_slug"),)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    organization: Mapped["Organization"] = relationship(back_populates="workspaces")
    departments: Mapped[list["Department"]] = relationship(back_populates="workspace")


class Department(TenantModel):
    """Organizational department within a workspace."""

    __tablename__ = "departments"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50))

    workspace: Mapped["Workspace"] = relationship(back_populates="departments")
    teams: Mapped[list["Team"]] = relationship(back_populates="department")


class Team(TenantModel):
    """Team unit within a department."""

    __tablename__ = "teams"

    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    department: Mapped[Optional["Department"]] = relationship(back_populates="teams")
    members: Mapped[list["TeamMember"]] = relationship(back_populates="team")


class TeamMember(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Many-to-many: users ↔ teams."""

    __tablename__ = "team_members"
    __table_args__ = (UniqueConstraint("team_id", "user_id", name="uq_team_members_team_user"),)

    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[Optional[str]] = mapped_column(String(50))

    team: Mapped["Team"] = relationship(back_populates="members")


class Role(TenantModel):
    """RBAC role definition per organization."""

    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_roles_org_name"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    permissions: Mapped[list["RolePermission"]] = relationship(back_populates="role")


class Permission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Global permission catalog (not tenant-scoped)."""

    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)


class RolePermission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Maps roles to permissions."""

    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permissions"),)

    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)
    permission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), index=True)

    role: Mapped["Role"] = relationship(back_populates="permissions")


class OrganizationMember(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """User membership in an organization."""

    __tablename__ = "organization_members"
    __table_args__ = (UniqueConstraint("organization_id", "user_id", name="uq_org_members"),)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("roles.id", ondelete="SET NULL"))
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UserRole(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Additional role assignments for a user within an org."""

    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("organization_id", "user_id", "role_id", name="uq_user_roles"),)

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)


class Invitation(TenantModel):
    """Pending user invitations."""

    __tablename__ = "invitations"

    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    role_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("roles.id", ondelete="SET NULL"))
    invited_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(default=InvitationStatus.PENDING, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SubscriptionPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Global subscription plan catalog."""

    __tablename__ = "subscription_plans"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tier: Mapped[SubscriptionTier] = mapped_column(nullable=False)
    price_monthly: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_yearly: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    max_users: Mapped[int] = mapped_column(Integer, default=5)
    max_customers: Mapped[int] = mapped_column(Integer, default=10000)
    stripe_product_id: Mapped[Optional[str]] = mapped_column(String(128), unique=True)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(128), unique=True)
    features: Mapped[dict] = mapped_column(JSONB, default=dict)


class Subscription(TenantModel):
    """Organization subscription state."""

    __tablename__ = "subscriptions"

    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subscription_plans.id"), index=True)
    status: Mapped[SubscriptionStatus] = mapped_column(default=SubscriptionStatus.TRIALING, index=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cancel_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    organization: Mapped["Organization"] = relationship(back_populates="subscriptions")
    plan: Mapped["SubscriptionPlan"] = relationship()


class BillingAccount(TenantModel):
    """Billing profile for an organization."""

    __tablename__ = "billing_accounts"

    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(128), unique=True)
    billing_email: Mapped[str] = mapped_column(String(320), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    address: Mapped[dict] = mapped_column(JSONB, default=dict)

    organization: Mapped["Organization"] = relationship(back_populates="billing_accounts")


class ApiKey(TenantModel):
    """Organization API keys."""

    __tablename__ = "api_keys"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    scopes: Mapped[list] = mapped_column(JSONB, default=list)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))


class FeatureFlag(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Global feature flag definitions."""

    __tablename__ = "feature_flags"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    default_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    scope: Mapped[FeatureFlagScope] = mapped_column(default=FeatureFlagScope.GLOBAL)


class OrganizationFeatureFlag(TenantModel):
    """Per-organization feature flag overrides."""

    __tablename__ = "organization_feature_flags"
    __table_args__ = (UniqueConstraint("organization_id", "feature_flag_id", name="uq_org_feature_flags"),)

    feature_flag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("feature_flags.id", ondelete="CASCADE"))
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
