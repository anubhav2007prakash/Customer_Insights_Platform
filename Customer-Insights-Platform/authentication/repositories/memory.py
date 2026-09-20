"""In-memory repositories for auth unit tests and local service verification."""

from __future__ import annotations

import copy
import uuid
from collections.abc import MutableSequence
from datetime import datetime
from types import TracebackType
from typing import Self

from authentication.repositories.interfaces import (
    AuditRepository,
    NotificationRepository,
    OrganizationRepository,
    RoleRepository,
    SessionRepository,
    TokenRepository,
    UserRepository,
)
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


class MemoryAuthStore:
    """Mutable in-memory auth store."""

    def __init__(self) -> None:
        self.users: list[User] = []
        self.profiles: list[UserProfile] = []
        self.preferences: list[UserPreference] = []
        self.password_history: list[PasswordHistory] = []
        self.organizations: list[Organization] = []
        self.workspaces: list[Workspace] = []
        self.members: list[OrganizationMember] = []
        self.roles: list[Role] = []
        self.user_roles: list[UserRole] = []
        self.sessions: list[UserSession] = []
        self.email_tokens: list[EmailVerificationToken] = []
        self.password_tokens: list[PasswordResetToken] = []
        self.audit_logs: list[AuditLog] = []
        self.security_events: list[SecurityEvent] = []
        self.login_history: list[LoginHistory] = []
        self.notifications: list[Notification] = []
        self.notification_settings: list[NotificationSetting] = []


class MemoryUserRepository(UserRepository):
    def __init__(self, store: MemoryAuthStore) -> None:
        self.store = store

    def get_by_email(self, email: str) -> User | None:
        return _first(self.store.users, lambda u: u.email == email)

    def get_by_username(self, username: str) -> User | None:
        return _first(self.store.users, lambda u: u.username == username)

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        user = _first(self.store.users, lambda u: u.id == user_id)
        if user:
            user.profile = _first(self.store.profiles, lambda p: p.user_id == user.id)
        return user

    def add(self, user: User) -> User:
        _append(self.store.users, user)
        return user

    def add_profile(self, profile: UserProfile) -> UserProfile:
        _append(self.store.profiles, profile)
        user = self.get_by_id(profile.user_id)
        if user:
            user.profile = profile
        return profile

    def add_preference(self, preference: UserPreference) -> UserPreference:
        _append(self.store.preferences, preference)
        return preference

    def add_password_history(self, history: PasswordHistory) -> PasswordHistory:
        _append(self.store.password_history, history)
        return history

    def password_history(self, user_id: uuid.UUID, limit: int) -> list[PasswordHistory]:
        rows = [row for row in self.store.password_history if row.user_id == user_id]
        return rows[-limit:][::-1]


class MemoryOrganizationRepository(OrganizationRepository):
    def __init__(self, store: MemoryAuthStore) -> None:
        self.store = store

    def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
        return _first(self.store.organizations, lambda o: o.id == organization_id)

    def get_by_slug(self, slug: str) -> Organization | None:
        return _first(self.store.organizations, lambda o: o.slug == slug and o.deleted_at is None)

    def add(self, organization: Organization) -> Organization:
        _append(self.store.organizations, organization)
        return organization

    def add_workspace(self, workspace: Workspace) -> Workspace:
        _append(self.store.workspaces, workspace)
        return workspace

    def add_member(self, member: OrganizationMember) -> OrganizationMember:
        _append(self.store.members, member)
        return member

    def get_member(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> OrganizationMember | None:
        return _first(
            self.store.members,
            lambda m: m.organization_id == organization_id and m.user_id == user_id and m.deleted_at is None,
        )

    def owner_count(self, organization_id: uuid.UUID) -> int:
        return sum(
            1
            for member in self.store.members
            if member.organization_id == organization_id and member.is_owner and member.deleted_at is None
        )


class MemoryRoleRepository(RoleRepository):
    def __init__(self, store: MemoryAuthStore) -> None:
        self.store = store

    def get_by_name(self, organization_id: uuid.UUID, name: str) -> Role | None:
        return _first(self.store.roles, lambda r: r.organization_id == organization_id and r.name == name)

    def add(self, role: Role) -> Role:
        _append(self.store.roles, role)
        return role

    def assign(self, assignment: UserRole) -> UserRole:
        _append(self.store.user_roles, assignment)
        return assignment


class MemorySessionRepository(SessionRepository):
    def __init__(self, store: MemoryAuthStore) -> None:
        self.store = store

    def add(self, session: UserSession) -> UserSession:
        _append(self.store.sessions, session)
        return session

    def get_active_by_token_hash(self, token_hash: str, now: datetime) -> UserSession | None:
        return _first(
            self.store.sessions,
            lambda s: s.token_hash == token_hash and s.revoked_at is None and s.expires_at > now,
        )

    def revoke(self, session: UserSession, revoked_at: datetime) -> None:
        session.revoked_at = revoked_at

    def revoke_all_for_user(self, user_id: uuid.UUID, revoked_at: datetime) -> int:
        count = 0
        for session in self.store.sessions:
            if session.user_id == user_id and session.revoked_at is None:
                session.revoked_at = revoked_at
                count += 1
        return count


class MemoryTokenRepository(TokenRepository):
    def __init__(self, store: MemoryAuthStore) -> None:
        self.store = store

    def add_email_verification(self, token: EmailVerificationToken) -> EmailVerificationToken:
        _append(self.store.email_tokens, token)
        return token

    def get_email_verification(self, token_hash: str, now: datetime) -> EmailVerificationToken | None:
        return _first(
            self.store.email_tokens,
            lambda t: t.token_hash == token_hash and t.used_at is None and t.expires_at > now,
        )

    def add_password_reset(self, token: PasswordResetToken) -> PasswordResetToken:
        _append(self.store.password_tokens, token)
        return token

    def get_password_reset(self, token_hash: str, now: datetime) -> PasswordResetToken | None:
        return _first(
            self.store.password_tokens,
            lambda t: t.token_hash == token_hash and t.used_at is None and t.expires_at > now,
        )


class MemoryAuditRepository(AuditRepository):
    def __init__(self, store: MemoryAuthStore) -> None:
        self.store = store

    def add_audit(self, audit_log: AuditLog) -> AuditLog:
        _append(self.store.audit_logs, audit_log)
        return audit_log

    def add_security_event(self, security_event: SecurityEvent) -> SecurityEvent:
        _append(self.store.security_events, security_event)
        return security_event

    def add_login_history(self, login_history: LoginHistory) -> LoginHistory:
        _append(self.store.login_history, login_history)
        return login_history


class MemoryNotificationRepository(NotificationRepository):
    def __init__(self, store: MemoryAuthStore) -> None:
        self.store = store

    def add(self, notification: Notification) -> Notification:
        _append(self.store.notifications, notification)
        return notification

    def add_setting(self, setting: NotificationSetting) -> NotificationSetting:
        _append(self.store.notification_settings, setting)
        return setting


class MemoryAuthUnitOfWork:
    """In-memory transaction boundary with rollback snapshot support."""

    _default_store: MemoryAuthStore | None = None

    def __init__(self, store: MemoryAuthStore | None = None) -> None:
        if store is not None:
            self.store = store
        else:
            if MemoryAuthUnitOfWork._default_store is None:
                MemoryAuthUnitOfWork._default_store = MemoryAuthStore()
            self.store = MemoryAuthUnitOfWork._default_store
        self._snapshot: MemoryAuthStore | None = None
        self.users = MemoryUserRepository(self.store)
        self.organizations = MemoryOrganizationRepository(self.store)
        self.roles = MemoryRoleRepository(self.store)
        self.sessions = MemorySessionRepository(self.store)
        self.tokens = MemoryTokenRepository(self.store)
        self.audit = MemoryAuditRepository(self.store)
        self.notifications = MemoryNotificationRepository(self.store)

    @classmethod
    def reset_store(cls) -> None:
        """Clear the shared in-memory store."""
        cls._default_store = MemoryAuthStore()

    def __enter__(self) -> Self:
        self._snapshot = copy.deepcopy(self.store)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self) -> None:
        self._snapshot = None

    def rollback(self) -> None:
        if self._snapshot is not None:
            self.store.__dict__.update(copy.deepcopy(self._snapshot.__dict__))
            self._snapshot = None


def _append(collection: MutableSequence, item):
    collection.append(item)


def _first(collection, predicate):
    return next((item for item in collection if predicate(item)), None)
