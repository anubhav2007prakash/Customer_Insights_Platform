"""SQLAlchemy-backed repositories for authorization service."""
from __future__ import annotations

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.session import SessionLocal
from database.models.tenant import (
    Role,
    Permission,
    RolePermission,
    UserRole,
    OrganizationMember,
    TeamMember,
    FeatureFlag,
    OrganizationFeatureFlag,
)
from authorization.models.role_hierarchy import RoleHierarchy


class AuthorizationRepository:
    def __init__(self, session: Session | None = None):
        self.session = session or SessionLocal()
        self._own_session = session is None

    def get_user_org_membership(self, organization_id, user_id) -> Optional[OrganizationMember]:
        return self.session.scalars(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
                OrganizationMember.deleted_at.is_(None),
            )
        ).first()

    def get_user_roles(self, organization_id, user_id) -> list[UserRole]:
        return list(
            self.session.scalars(
                select(UserRole).where(
                    UserRole.organization_id == organization_id,
                    UserRole.user_id == user_id,
                    UserRole.deleted_at.is_(None),
                )
            ).all()
        )

    def get_roles_permissions(self, role_ids: list) -> list[Permission]:
        if not role_ids:
            return []
        stmt = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id.in_(role_ids))
        )
        return list(self.session.scalars(stmt).all())

    def get_role_by_id(self, role_id):
        return self.session.get(Role, role_id)

    def get_role_hierarchy_parents(self, role_id) -> list[RoleHierarchy]:
        return list(self.session.scalars(select(RoleHierarchy).where(RoleHierarchy.child_role_id == role_id)).all())

    def get_feature_flag(self, key: str):
        return self.session.scalars(select(FeatureFlag).where(FeatureFlag.key == key)).first()

    def get_org_feature_flag(self, organization_id, feature_flag_id):
        return self.session.scalars(
            select(OrganizationFeatureFlag).where(
                OrganizationFeatureFlag.organization_id == organization_id,
                OrganizationFeatureFlag.feature_flag_id == feature_flag_id,
            )
        ).first()

    def close(self):
        if self._own_session:
            self.session.close()
