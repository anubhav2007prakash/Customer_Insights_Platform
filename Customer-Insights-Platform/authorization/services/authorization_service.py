"""Centralized Authorization service implementing permission checks."""
from __future__ import annotations

from functools import lru_cache
from typing import Iterable

from authorization.repositories.sqlalchemy import AuthorizationRepository
from database.models.tenant import Role
from authorization.models.role_hierarchy import RoleHierarchy
from authorization import context
from authorization.exceptions import PermissionDeniedException


class AuthorizationService:
    """Core authorization logic. Use repository adapters for persistence.

    Example usage:
        svc = AuthorizationService()
        svc.has_permission(user_id, org_id, "customer.read")
    """

    def __init__(self, repo: AuthorizationRepository | None = None):
        self.repo = repo or AuthorizationRepository()

    def _gather_role_ids(self, organization_id, user_id) -> list:
        # organization member role + user_roles
        role_ids = []
        membership = self.repo.get_user_org_membership(organization_id, user_id)
        if membership and membership.role_id:
            role_ids.append(membership.role_id)
        user_roles = self.repo.get_user_roles(organization_id, user_id)
        for ur in user_roles:
            role_ids.append(ur.role_id)
        return role_ids

    def _expand_inherited_roles(self, role_ids: Iterable) -> list:
        # depth-first expansion using RoleHierarchy
        expanded = set()
        stack = list(role_ids)
        while stack:
            r = stack.pop()
            if r in expanded:
                continue
            expanded.add(r)
            parents = self.repo.get_role_hierarchy_parents(r)
            for p in parents:
                stack.append(p.parent_role_id)
        return list(expanded)

    def _permissions_for_roles(self, role_ids: Iterable) -> set[str]:
        perms = self.repo.get_roles_permissions(list(role_ids))
        return {p.code for p in perms}

    def has_role(self, user_id, organization_id, role_name: str) -> bool:
        role_ids = self._gather_role_ids(organization_id, user_id)
        for rid in role_ids:
            role = self.repo.get_role_by_id(rid)
            if role and getattr(role, "name", None) == role_name:
                return True
        return False

    def has_permission(self, user_id, organization_id, permission_code: str, *, resource_owner_id=None) -> bool:
        # Tenant isolation check
        # If resource_owner_id provided and belongs to different org, deny
        # (caller should ensure resource_org_id if needed)

        role_ids = self._gather_role_ids(organization_id, user_id)
        if not role_ids:
            return False

        # expand inheritance
        expanded = self._expand_inherited_roles(role_ids)
        perms = self._permissions_for_roles(expanded)

        if permission_code in perms:
            return True

        # ownership check: if user is owner of resource and permission pattern allows owner
        if resource_owner_id and resource_owner_id == user_id:
            # allow if permission_code has suffix ".own" or caller uses separate pattern
            owner_variant = f"{permission_code}.own"
            if owner_variant in perms:
                return True

        return False

    def require_permission(self, user_id, organization_id, permission_code: str, *, resource_owner_id=None) -> None:
        if not self.has_permission(user_id, organization_id, permission_code, resource_owner_id=resource_owner_id):
            raise PermissionDeniedException(f"Missing permission: {permission_code}")

    def is_feature_enabled(self, organization_id, feature_key: str) -> bool:
        ff = self.repo.get_feature_flag(feature_key)
        if not ff:
            return False
        org_flag = self.repo.get_org_feature_flag(organization_id, ff.id)
        if org_flag is None:
            return bool(ff.default_enabled)
        return bool(org_flag.is_enabled)

    def invalidate_caches(self):
        # placeholder for cache invalidation — if using lru_cache, we can clear here
        try:
            self._permissions_for_roles.cache_clear()  # type: ignore[attr-defined]
        except Exception:
            pass