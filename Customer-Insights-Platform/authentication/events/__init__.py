"""Authentication domain events."""

from authentication.events.auth_events import (
    AccountLocked,
    EmailVerified,
    LoginFailed,
    LoginSucceeded,
    LogoutCompleted,
    PasswordChanged,
    PasswordResetRequested,
    UserRegistered,
)

__all__ = [
    "AccountLocked",
    "EmailVerified",
    "LoginFailed",
    "LoginSucceeded",
    "LogoutCompleted",
    "PasswordChanged",
    "PasswordResetRequested",
    "UserRegistered",
]
