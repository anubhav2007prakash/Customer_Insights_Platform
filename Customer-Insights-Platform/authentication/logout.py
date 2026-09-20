"""Compatibility exports for logout workflows."""

from authentication.schemas import LogoutRequest
from authentication.services.login import AuthenticationService

__all__ = ["AuthenticationService", "LogoutRequest"]
