"""Compatibility exports for access-control decorators."""

from authentication.decorators import require_authenticated_session, require_permission

__all__ = ["require_authenticated_session", "require_permission"]
