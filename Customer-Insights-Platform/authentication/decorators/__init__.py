"""Authentication decorators."""

from authentication.decorators.access import require_authenticated_session, require_permission

__all__ = ["require_authenticated_session", "require_permission"]
