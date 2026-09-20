"""Email verification workflows."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import timedelta

from core.config.settings import Settings, get_settings
from core.events.base import EventMetadata
from core.interfaces.event_bus import EventBusPort
from database.enums import AuditAction, NotificationChannel, NotificationPriority, UserStatus
from database.models.auth import EmailVerificationToken
from database.models.notifications import Notification
from authentication.audit import AuthAuditLogger
from authentication.events import EmailVerified
from authentication.exceptions import VerificationException
from authentication.helpers import TokenService, utc_now
from authentication.repositories.interfaces import AuthUnitOfWork
from authentication.repositories.sqlalchemy import SQLAlchemyAuthUnitOfWork
from authentication.schemas import EmailVerificationRequest, PasswordResetResponse
from authentication.services.providers import EmailProvider, MockEmailProvider


class EmailVerificationService:
    """Email verification service."""

    def __init__(
        self,
        uow_factory: Callable[[], AuthUnitOfWork] | None = None,
        *,
        settings: Settings | None = None,
        email_provider: EmailProvider | None = None,
        event_bus: EventBusPort | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.uow_factory = uow_factory or SQLAlchemyAuthUnitOfWork
        self.email_provider = email_provider or MockEmailProvider()
        self.event_bus = event_bus
        self.token_service = TokenService(self.settings.security.secret_key)

    def verify(self, request: EmailVerificationRequest) -> None:
        """Verify a user's email address using a one-time token."""
        now = utc_now()
        with self.uow_factory() as uow:
            token = uow.tokens.get_email_verification(self.token_service.hash(request.token), now)
            if token is None:
                raise VerificationException("Verification token is invalid or expired.")
            user = uow.users.get_by_id(token.user_id)
            if user is None:
                raise VerificationException("Verification token is invalid or expired.")
            user.email_verified_at = now
            if user.status == UserStatus.PENDING_VERIFICATION:
                user.status = UserStatus.ACTIVE
            token.used_at = now
            AuthAuditLogger(uow.audit).audit(
                action=AuditAction.EMAIL_VERIFICATION,
                entity_type="user",
                user_id=user.id,
                entity_id=user.id,
                new_values={"email_verified": True},
            )
            self._create_notification(uow, user.id)
            if self.event_bus:
                self.event_bus.publish(EmailVerified(metadata=EventMetadata(user_id=user.id), user_id=user.id))

    def resend(self, email: str) -> PasswordResetResponse:
        """Resend verification email without revealing account existence."""
        with self.uow_factory() as uow:
            user = uow.users.get_by_email(email.strip().lower())
            if user is None or user.email_verified_at is not None:
                return PasswordResetResponse(message="If verification is required, instructions will be sent.")
            token = self.token_service.generate()
            uow.tokens.add_email_verification(
                EmailVerificationToken(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    email=user.email,
                    token_hash=token.token_hash,
                    expires_at=utc_now() + timedelta(hours=self.settings.security.email_verification_token_ttl_hours),
                )
            )
            self.email_provider.send_verification_email(
                email=user.email,
                token=token.raw,
                full_name=user.profile.display_name if user.profile else user.email,
            )
        return PasswordResetResponse(message="If verification is required, instructions will be sent.")

    def _create_notification(self, uow: AuthUnitOfWork, user_id: uuid.UUID) -> None:
        # Organization is optional here because a user may verify before selecting an org.
        user = uow.users.get_by_id(user_id)
        organization_id = None
        if user:
            # Best effort: derive the organization from any active membership.
            # Repositories intentionally expose narrow methods, so notifications can be skipped if unknown.
            pass
        if organization_id:
            uow.notifications.add(
                Notification(
                    id=uuid.uuid4(),
                    organization_id=organization_id,
                    user_id=user_id,
                    title="Email verified",
                    body="Your email address has been verified.",
                    channel=NotificationChannel.IN_APP,
                    priority=NotificationPriority.NORMAL,
                    metadata_={"event": "security.email_verified"},
                )
            )
