"""Role-based access control helpers."""

from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from core.exceptions.base import AuthorizationError
from core.types.common import TenantContext

F = TypeVar("F", bound=Callable)


class PermissionChecker:
    """Injectable RBAC permission checker."""

    def has_permission(self, ctx: TenantContext, permission: str) -> bool:
        """Check if context has the required permission."""
        return permission in ctx.permissions or "admin.full" in ctx.permissions

    def require(self, ctx: TenantContext, permission: str) -> None:
        """Raise AuthorizationError if permission missing."""
        if not self.has_permission(ctx, permission):
            raise AuthorizationError(
                message=f"Missing required permission: {permission}",
                details={"permission": permission},
            )


def require_permission(permission: str) -> Callable[[F], F]:
    """
    Decorator for service methods requiring a permission.

    Expects `ctx: TenantContext` as first argument after self.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx = kwargs.get("ctx") or (args[1] if len(args) > 1 else None)
            if ctx is None or not isinstance(ctx, TenantContext):
                raise AuthorizationError(message="Tenant context required.")
            PermissionChecker().require(ctx, permission)
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
