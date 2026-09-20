"""Repository ports for authentication services."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from types import TracebackType
from typing import Self

from database.models.auth import (
    EmailVerificationToken,
    LoginHistory,
    NotificationSetting,
    PasswordHistory,
    PasswordResetToken,
    User,
    UserProfile,
    UserPreference,
    UserSession,
)
from database.models.notifications import Notification
from database.models.security import AuditLog, SecurityEvent
from database.models.tenant import Organization, OrganizationMember, Role, UserRole, Workspace


class UserRepository(ABC):
    """User persistence port."""

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        ...

    @abstractmethod
    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        ...

    @abstractmethod
    def add(self, user: User) -> User:
        ...

    @abstractmethod
    def add_profile(self, profile: UserProfile) -> UserProfile:
        ...

    @abstractmethod
    def add_preference(self, preference: UserPreference) -> UserPreference:
        ...

    @abstractmethod
    def add_password_history(self, history: PasswordHistory) -> PasswordHistory:
        ...

    @abstractmethod
    def password_history(self, user_id: uuid.UUID, limit: int) -> list[PasswordHistory]:
        ...


class OrganizationRepository(ABC):
    """Organization persistence port."""

    @abstractmethod
    def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
        ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> Organization | None:
        ...

    @abstractmethod
    def add(self, organization: Organization) -> Organization:
        ...

    @abstractmethod
    def add_workspace(self, workspace: Workspace) -> Workspace:
        ...

    @abstractmethod
    def add_member(self, member: OrganizationMember) -> OrganizationMember:
        ...

    @abstractmethod
    def get_member(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> OrganizationMember | None:
        ...

    @abstractmethod
    def owner_count(self, organization_id: uuid.UUID) -> int:
        ...


class RoleRepository(ABC):
    """RBAC role persistence port."""

    @abstractmethod
    def get_by_name(self, organization_id: uuid.UUID, name: str) -> Role | None:
        ...

    @abstractmethod
    def add(self, role: Role) -> Role:
        ...

    @abstractmethod
    def assign(self, assignment: UserRole) -> UserRole:
        ...


class SessionRepository(ABC):
    """Session persistence port."""

    @abstractmethod
    def add(self, session: UserSession) -> UserSession:
        ...

    @abstractmethod
    def get_active_by_token_hash(self, token_hash: str, now: datetime) -> UserSession | None:
        ...

    @abstractmethod
    def revoke(self, session: UserSession, revoked_at: datetime) -> None:
        ...

    @abstractmethod
    def revoke_all_for_user(self, user_id: uuid.UUID, revoked_at: datetime) -> int:
        ...


class TokenRepository(ABC):
    """Verification and password reset token persistence port."""

    @abstractmethod
    def add_email_verification(self, token: EmailVerificationToken) -> EmailVerificationToken:
        ...

    @abstractmethod
    def get_email_verification(self, token_hash: str, now: datetime) -> EmailVerificationToken | None:
        ...

    @abstractmethod
    def add_password_reset(self, token: PasswordResetToken) -> PasswordResetToken:
        ...

    @abstractmethod
    def get_password_reset(self, token_hash: str, now: datetime) -> PasswordResetToken | None:
        ...


class AuditRepository(ABC):
    """Audit persistence port."""

    @abstractmethod
    def add_audit(self, audit_log: AuditLog) -> AuditLog:
        ...

    @abstractmethod
    def add_security_event(self, security_event: SecurityEvent) -> SecurityEvent:
        ...

    @abstractmethod
    def add_login_history(self, login_history: LoginHistory) -> LoginHistory:
        ...


class NotificationRepository(ABC):
    """Notification persistence port."""

    @abstractmethod
    def add(self, notification: Notification) -> Notification:
        ...

    @abstractmethod
    def add_setting(self, setting: NotificationSetting) -> NotificationSetting:
        ...


class AuthUnitOfWork(ABC):
    """Transactional repository bundle for authentication workflows."""

    users: UserRepository
    organizations: OrganizationRepository
    roles: RoleRepository
    sessions: SessionRepository
    tokens: TokenRepository
    audit: AuditRepository
    notifications: NotificationRepository

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...

    @abstractmethod
    def __enter__(self) -> Self:
        ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        ...
