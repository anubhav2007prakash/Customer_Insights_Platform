"""Login, lockout, and logout workflows."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import timedelta

from core.config.settings import Settings, get_settings
from core.events.base import EventMetadata
from core.interfaces.event_bus import EventBusPort
from database.enums import AuditAction, UserStatus
from database.models.auth import User, UserSession
from authentication.audit import AuthAuditLogger
from authentication.events import AccountLocked, LoginFailed, LoginSucceeded, LogoutCompleted
from authentication.exceptions import InvalidCredentialsException
from authentication.helpers import PasswordHasher, TokenService, normalize_email, normalize_username, utc_now
from authentication.policies import AccountPolicy
from authentication.repositories.interfaces import AuthUnitOfWork
from authentication.repositories.sqlalchemy import SQLAlchemyAuthUnitOfWork
from authentication.schemas import LoginRequest, LoginResponse, LogoutRequest, SessionInfo


class AuthenticationService:
    """Enterprise authentication service."""

    def __init__(
        self,
        uow_factory: Callable[[], AuthUnitOfWork] | None = None,
        *,
        settings: Settings | None = None,
        event_bus: EventBusPort | None = None,
        password_hasher: PasswordHasher | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.uow_factory = uow_factory or SQLAlchemyAuthUnitOfWork
        self.event_bus = event_bus
        self.password_hasher = password_hasher or PasswordHasher()
        self.token_service = TokenService(self.settings.security.secret_key)
        self.account_policy = AccountPolicy()

    def login(self, request: LoginRequest) -> LoginResponse:
        """Authenticate by email or username and create a persisted session."""
        now = utc_now()
        identifier = request.identifier.strip()
        with self.uow_factory() as uow:
            user = self._find_user(uow, identifier)
            organization = None
            organization_id = request.organization_id
            if request.organization_slug:
                organization = uow.organizations.get_by_slug(request.organization_slug)
                organization_id = organization.id if organization else None
            elif organization_id:
                organization = uow.organizations.get_by_id(organization_id)

            if not user or not self.password_hasher.verify(request.password, user.password_hash):
                self._record_failed_login(uow, user, organization_id, request, "invalid_credentials")
                raise InvalidCredentialsException()

            if organization_id:
                if organization is None:
                    self._record_failed_login(uow, user, organization_id, request, "organization_not_found")
                    raise InvalidCredentialsException()
                self.account_policy.assert_organization_can_authenticate(organization)
                if not uow.organizations.get_member(organization_id, user.id):
                    self._record_failed_login(uow, user, organization_id, request, "not_org_member")
                    raise InvalidCredentialsException()

            self.account_policy.assert_user_can_authenticate(
                user,
                now=now,
                require_verified_email=self.settings.security.require_verified_email,
            )
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login_at = now

            session_token = self.token_service.generate()
            expires_at = now + (
                timedelta(days=self.settings.security.remember_me_ttl_days)
                if request.remember_me
                else timedelta(hours=self.settings.security.session_ttl_hours)
            )
            session = uow.sessions.add(
                UserSession(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    organization_id=organization_id,
                    token_hash=session_token.token_hash,
                    device_fingerprint=request.device_fingerprint,
                    device_name=request.device_name,
                    remember_me=request.remember_me,
                    ip_address=request.ip_address,
                    user_agent=request.user_agent,
                    last_seen_at=now,
                    expires_at=expires_at,
                )
            )
            audit = AuthAuditLogger(uow.audit)
            audit.login_history(
                user_id=user.id,
                organization_id=organization_id,
                success=True,
                ip_address=request.ip_address,
                user_agent=request.user_agent,
            )
            audit.audit(
                action=AuditAction.LOGIN,
                entity_type="session",
                organization_id=organization_id,
                user_id=user.id,
                entity_id=session.id,
                ip_address=request.ip_address,
                user_agent=request.user_agent,
            )
            if self.event_bus:
                self.event_bus.publish(
                    LoginSucceeded(
                        metadata=EventMetadata(organization_id=organization_id, user_id=user.id),
                        user_id=user.id,
                        session_id=session.id,
                    )
                )
            return LoginResponse(
                session=SessionInfo(
                    session_token=session_token.raw,
                    expires_at=expires_at,
                    user_id=user.id,
                    organization_id=organization_id,
                    remember_me=request.remember_me,
                ),
                email=user.email,
                username=user.username,
                status=user.status.value,
            )

    def logout(self, request: LogoutRequest) -> None:
        """Securely revoke a session token."""
        now = utc_now()
        token_hash = self.token_service.hash(request.session_token)
        with self.uow_factory() as uow:
            session = uow.sessions.get_active_by_token_hash(token_hash, now)
            if session is None:
                return
            uow.sessions.revoke(session, now)
            AuthAuditLogger(uow.audit).audit(
                action=AuditAction.LOGOUT,
                entity_type="session",
                organization_id=session.organization_id,
                user_id=session.user_id,
                entity_id=session.id,
            )
            if self.event_bus:
                self.event_bus.publish(
                    LogoutCompleted(
                        metadata=EventMetadata(organization_id=session.organization_id, user_id=session.user_id),
                        user_id=session.user_id,
                        session_id=session.id,
                    )
                )

    def _find_user(self, uow: AuthUnitOfWork, identifier: str) -> User | None:
        if "@" in identifier:
            return uow.users.get_by_email(normalize_email(identifier))
        username = normalize_username(identifier)
        return uow.users.get_by_username(username) if username else None

    def _record_failed_login(
        self,
        uow: AuthUnitOfWork,
        user: User | None,
        organization_id: uuid.UUID | None,
        request: LoginRequest,
        reason: str,
    ) -> None:
        audit = AuthAuditLogger(uow.audit)
        if user is not None:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= self.settings.security.max_login_attempts:
                user.locked_until = utc_now() + timedelta(minutes=self.settings.security.lockout_minutes)
                user.status = UserStatus.LOCKED
                audit.audit(
                    action=AuditAction.ACCOUNT_LOCK,
                    entity_type="user",
                    organization_id=organization_id,
                    user_id=user.id,
                    entity_id=user.id,
                    new_values={"reason": reason, "locked_until": user.locked_until.isoformat()},
                    ip_address=request.ip_address,
                    user_agent=request.user_agent,
                )
                if self.event_bus:
                    self.event_bus.publish(
                        AccountLocked(
                            metadata=EventMetadata(organization_id=organization_id, user_id=user.id),
                            user_id=user.id,
                            reason=reason,
                        )
                    )
            audit.login_history(
                user_id=user.id,
                organization_id=organization_id,
                success=False,
                ip_address=request.ip_address,
                user_agent=request.user_agent,
                failure_reason=reason,
            )
        audit.security_event(
            event_type="login_failure",
            description="Failed login attempt.",
            severity="warning",
            organization_id=organization_id,
            user_id=user.id if user else None,
            ip_address=request.ip_address,
            metadata={"identifier": request.identifier, "reason": reason},
        )
        if self.event_bus:
            self.event_bus.publish(LoginFailed(identifier=request.identifier, reason=reason))
