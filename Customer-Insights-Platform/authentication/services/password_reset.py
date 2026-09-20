"""Password reset and password change workflows."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import timedelta

from core.config.settings import Settings, get_settings
from core.events.base import EventMetadata
from core.interfaces.event_bus import EventBusPort
from database.enums import AuditAction
from database.models.auth import PasswordHistory, PasswordResetToken, User
from authentication.audit import AuthAuditLogger
from authentication.events import PasswordChanged, PasswordResetRequested
from authentication.exceptions import InvalidCredentialsException, PasswordPolicyException, PasswordResetException
from authentication.helpers import PasswordHasher, TokenService, utc_now
from authentication.repositories.interfaces import AuthUnitOfWork
from authentication.repositories.sqlalchemy import SQLAlchemyAuthUnitOfWork
from authentication.schemas import (
    ForgotPasswordRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetResponse,
)
from authentication.services.providers import EmailProvider, MockEmailProvider
from authentication.validators import PasswordPolicyValidator


class PasswordResetService:
    """Secure password reset and change service."""

    def __init__(
        self,
        uow_factory: Callable[[], AuthUnitOfWork] | None = None,
        *,
        settings: Settings | None = None,
        email_provider: EmailProvider | None = None,
        event_bus: EventBusPort | None = None,
        password_hasher: PasswordHasher | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.uow_factory = uow_factory or SQLAlchemyAuthUnitOfWork
        self.email_provider = email_provider or MockEmailProvider()
        self.event_bus = event_bus
        self.password_hasher = password_hasher or PasswordHasher()
        self.password_validator = PasswordPolicyValidator()
        self.token_service = TokenService(self.settings.security.secret_key)

    def request_reset(self, request: ForgotPasswordRequest) -> PasswordResetResponse:
        """Create a reset token if the account exists; never reveal account existence."""
        with self.uow_factory() as uow:
            user = uow.users.get_by_email(str(request.email))
            if user is None:
                return PasswordResetResponse()
            token = self.token_service.generate()
            uow.tokens.add_password_reset(
                PasswordResetToken(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    token_hash=token.token_hash,
                    expires_at=utc_now() + timedelta(minutes=self.settings.security.password_reset_token_ttl_minutes),
                    requested_ip=request.ip_address,
                    user_agent=request.user_agent,
                )
            )
            AuthAuditLogger(uow.audit).audit(
                action=AuditAction.PASSWORD_RESET,
                entity_type="password_reset_token",
                user_id=user.id,
                entity_id=user.id,
                ip_address=request.ip_address,
                user_agent=request.user_agent,
                new_values={"requested": True},
            )
            self.email_provider.send_password_reset_email(email=user.email, token=token.raw, full_name=_display_name(user))
            if self.event_bus:
                self.event_bus.publish(PasswordResetRequested(email=user.email))
        return PasswordResetResponse()

    def reset_password(self, request: PasswordResetRequest) -> None:
        """Reset a password with a valid one-time token."""
        self.password_validator.validate(request.password)
        now = utc_now()
        token_hash = self.token_service.hash(request.token)
        with self.uow_factory() as uow:
            reset_token = uow.tokens.get_password_reset(token_hash, now)
            if reset_token is None:
                raise PasswordResetException("Reset token is invalid or expired.")
            user = uow.users.get_by_id(reset_token.user_id)
            if user is None:
                raise PasswordResetException("Reset token is invalid or expired.")
            self._assert_not_reused(uow, user, request.password)
            self._set_new_password(uow, user, request.password)
            reset_token.used_at = now
            uow.sessions.revoke_all_for_user(user.id, now)
            AuthAuditLogger(uow.audit).audit(
                action=AuditAction.PASSWORD_CHANGE,
                entity_type="user",
                user_id=user.id,
                entity_id=user.id,
                new_values={"source": "password_reset"},
            )
            self.email_provider.send_password_changed_email(email=user.email, full_name=_display_name(user))
            if self.event_bus:
                self.event_bus.publish(
                    PasswordChanged(metadata=EventMetadata(user_id=user.id), user_id=user.id)
                )

    def change_password(self, user_id: uuid.UUID, request: PasswordChangeRequest) -> None:
        """Authenticated password change."""
        self.password_validator.validate(request.new_password)
        with self.uow_factory() as uow:
            user = uow.users.get_by_id(user_id)
            if user is None or not self.password_hasher.verify(request.current_password, user.password_hash):
                raise InvalidCredentialsException()
            self._assert_not_reused(uow, user, request.new_password)
            self._set_new_password(uow, user, request.new_password)
            uow.sessions.revoke_all_for_user(user.id, utc_now())
            AuthAuditLogger(uow.audit).audit(
                action=AuditAction.PASSWORD_CHANGE,
                entity_type="user",
                user_id=user.id,
                entity_id=user.id,
                new_values={"source": "authenticated_change"},
            )
            self.email_provider.send_password_changed_email(email=user.email, full_name=_display_name(user))
            if self.event_bus:
                self.event_bus.publish(
                    PasswordChanged(metadata=EventMetadata(user_id=user.id), user_id=user.id)
                )

    def _assert_not_reused(self, uow: AuthUnitOfWork, user: User, password: str) -> None:
        for history in uow.users.password_history(user.id, self.settings.security.password_history_count):
            if self.password_hasher.verify(password, history.password_hash):
                raise PasswordPolicyException("Password was used recently.")

    def _set_new_password(self, uow: AuthUnitOfWork, user: User, password: str) -> None:
        now = utc_now()
        user.password_hash = self.password_hasher.hash(password)
        user.password_changed_at = now
        user.password_expires_at = now + timedelta(days=self.settings.security.password_expiration_days)
        uow.users.add_password_history(
            PasswordHistory(id=uuid.uuid4(), user_id=user.id, password_hash=user.password_hash)
        )


def _display_name(user: User) -> str | None:
    if user.profile and user.profile.display_name:
        return user.profile.display_name
    return None
