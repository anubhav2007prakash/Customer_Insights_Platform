"""Role-based access control primitives."""

from __future__ import annotations

from enum import StrEnum

from core.exceptions.base import AuthorizationError


class AuthPermission(StrEnum):
    """Canonical IAM permissions."""

    USERS_READ = "users.read"
    USERS_WRITE = "users.write"
    ROLES_MANAGE = "roles.manage"
    SETTINGS_MANAGE = "settings.manage"
    ADMIN_FULL = "admin.full"


class RBACService:
    """Small permission checker used by decorators and middleware."""

    def has_permission(self, permissions: set[str] | frozenset[str], permission: str) -> bool:
        return permission in permissions or AuthPermission.ADMIN_FULL.value in permissions

    def require(self, permissions: set[str] | frozenset[str], permission: str) -> None:
        if not self.has_permission(permissions, permission):
            raise AuthorizationError(
                message=f"Missing required permission: {permission}",
                details={"permission": permission},
            )
