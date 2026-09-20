"""SQLAlchemy authentication repositories."""

from __future__ import annotations

import uuid
from datetime import datetime
from types import TracebackType
from typing import Self

from sqlalchemy import func, select
from sqlalchemy.orm import Session

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
from database.session import SessionLocal


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy user repository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalars(select(User).where(User.email == email, User.deleted_at.is_(None))).first()

    def get_by_username(self, username: str) -> User | None:
        return self.session.scalars(select(User).where(User.username == username, User.deleted_at.is_(None))).first()

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.session.get(User, user_id)

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def add_profile(self, profile: UserProfile) -> UserProfile:
        self.session.add(profile)
        self.session.flush()
        return profile

    def add_preference(self, preference: UserPreference) -> UserPreference:
        self.session.add(preference)
        self.session.flush()
        return preference

    def add_password_history(self, history: PasswordHistory) -> PasswordHistory:
        self.session.add(history)
        self.session.flush()
        return history

    def password_history(self, user_id: uuid.UUID, limit: int) -> list[PasswordHistory]:
        stmt = (
            select(PasswordHistory)
            .where(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())


class SQLAlchemyOrganizationRepository(OrganizationRepository):
    """SQLAlchemy organization repository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
        return self.session.get(Organization, organization_id)

    def get_by_slug(self, slug: str) -> Organization | None:
        return self.session.scalars(
            select(Organization).where(Organization.slug == slug, Organization.deleted_at.is_(None))
        ).first()

    def add(self, organization: Organization) -> Organization:
        self.session.add(organization)
        self.session.flush()
        return organization

    def add_workspace(self, workspace: Workspace) -> Workspace:
        self.session.add(workspace)
        self.session.flush()
        return workspace

    def add_member(self, member: OrganizationMember) -> OrganizationMember:
        self.session.add(member)
        self.session.flush()
        return member

    def get_member(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> OrganizationMember | None:
        return self.session.scalars(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
                OrganizationMember.deleted_at.is_(None),
            )
        ).first()

    def owner_count(self, organization_id: uuid.UUID) -> int:
        return self.session.scalar(
            select(func.count()).select_from(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.is_owner.is_(True),
                OrganizationMember.deleted_at.is_(None),
            )
        ) or 0


class SQLAlchemyRoleRepository(RoleRepository):
    """SQLAlchemy role repository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_name(self, organization_id: uuid.UUID, name: str) -> Role | None:
        return self.session.scalars(
            select(Role).where(Role.organization_id == organization_id, Role.name == name, Role.deleted_at.is_(None))
        ).first()

    def add(self, role: Role) -> Role:
        self.session.add(role)
        self.session.flush()
        return role

    def assign(self, assignment: UserRole) -> UserRole:
        self.session.add(assignment)
        self.session.flush()
        return assignment


class SQLAlchemySessionRepository(SessionRepository):
    """SQLAlchemy session repository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, session: UserSession) -> UserSession:
        self.session.add(session)
        self.session.flush()
        return session

    def get_active_by_token_hash(self, token_hash: str, now: datetime) -> UserSession | None:
        return self.session.scalars(
            select(UserSession).where(
                UserSession.token_hash == token_hash,
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > now,
            )
        ).first()

    def revoke(self, session: UserSession, revoked_at: datetime) -> None:
        session.revoked_at = revoked_at
        self.session.flush()

    def revoke_all_for_user(self, user_id: uuid.UUID, revoked_at: datetime) -> int:
        sessions = self.session.scalars(
            select(UserSession).where(UserSession.user_id == user_id, UserSession.revoked_at.is_(None))
        ).all()
        for session in sessions:
            session.revoked_at = revoked_at
        self.session.flush()
        return len(sessions)


class SQLAlchemyTokenRepository(TokenRepository):
    """SQLAlchemy token repository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add_email_verification(self, token: EmailVerificationToken) -> EmailVerificationToken:
        self.session.add(token)
        self.session.flush()
        return token

    def get_email_verification(self, token_hash: str, now: datetime) -> EmailVerificationToken | None:
        return self.session.scalars(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == token_hash,
                EmailVerificationToken.used_at.is_(None),
                EmailVerificationToken.expires_at > now,
            )
        ).first()

    def add_password_reset(self, token: PasswordResetToken) -> PasswordResetToken:
        self.session.add(token)
        self.session.flush()
        return token

    def get_password_reset(self, token_hash: str, now: datetime) -> PasswordResetToken | None:
        return self.session.scalars(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
            )
        ).first()


class SQLAlchemyAuditRepository(AuditRepository):
    """SQLAlchemy audit repository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add_audit(self, audit_log: AuditLog) -> AuditLog:
        self.session.add(audit_log)
        self.session.flush()
        return audit_log

    def add_security_event(self, security_event: SecurityEvent) -> SecurityEvent:
        self.session.add(security_event)
        self.session.flush()
        return security_event

    def add_login_history(self, login_history: LoginHistory) -> LoginHistory:
        self.session.add(login_history)
        self.session.flush()
        return login_history


class SQLAlchemyNotificationRepository(NotificationRepository):
    """SQLAlchemy notification repository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, notification: Notification) -> Notification:
        self.session.add(notification)
        self.session.flush()
        return notification

    def add_setting(self, setting: NotificationSetting) -> NotificationSetting:
        self.session.add(setting)
        self.session.flush()
        return setting


class SQLAlchemyAuthUnitOfWork:
    """Transaction boundary for authentication workflows."""

    def __init__(self, session_factory=SessionLocal) -> None:
        self.session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self) -> Self:
        self.session = self.session_factory()
        self.users = SQLAlchemyUserRepository(self.session)
        self.organizations = SQLAlchemyOrganizationRepository(self.session)
        self.roles = SQLAlchemyRoleRepository(self.session)
        self.sessions = SQLAlchemySessionRepository(self.session)
        self.tokens = SQLAlchemyTokenRepository(self.session)
        self.audit = SQLAlchemyAuditRepository(self.session)
        self.notifications = SQLAlchemyNotificationRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type:
                self.rollback()
            else:
                self.commit()
        finally:
            if self.session:
                self.session.close()
                self.session = None

    def commit(self) -> None:
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        if self.session:
            self.session.rollback()
