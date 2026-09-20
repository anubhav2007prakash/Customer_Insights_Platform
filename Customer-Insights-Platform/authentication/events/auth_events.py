"""Authentication domain events."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from core.events.base import DomainEvent


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str = ""


@dataclass(frozen=True)
class LoginSucceeded(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    session_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class LoginFailed(DomainEvent):
    identifier: str = ""
    reason: str = ""


@dataclass(frozen=True)
class LogoutCompleted(DomainEvent):
    user_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None


@dataclass(frozen=True)
class PasswordResetRequested(DomainEvent):
    email: str = ""


@dataclass(frozen=True)
class PasswordChanged(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class EmailVerified(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class AccountLocked(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    reason: str = ""
