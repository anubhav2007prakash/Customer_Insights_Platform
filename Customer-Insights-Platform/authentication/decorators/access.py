"""Decorators for presentation and service boundaries."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

from core.exceptions.base import AuthenticationError
from authentication.permissions import RBACService

F = TypeVar("F", bound=Callable[..., Any])


def require_authenticated_session(func: F) -> F:
    """Require a `session` keyword argument or object with `user_id`."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        session = kwargs.get("session")
        if session is None and len(args) > 1:
            session = args[1]
        if session is None or getattr(session, "user_id", None) is None:
            raise AuthenticationError(message="Authenticated session required.")
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def require_permission(permission: str) -> Callable[[F], F]:
    """Require a `permissions` keyword argument or object attribute."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            permissions = kwargs.get("permissions")
            if permissions is None and len(args) > 1:
                permissions = getattr(args[1], "permissions", None)
            if permissions is None:
                raise AuthenticationError(message="Permission context required.")
            RBACService().require(set(permissions), permission)
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
