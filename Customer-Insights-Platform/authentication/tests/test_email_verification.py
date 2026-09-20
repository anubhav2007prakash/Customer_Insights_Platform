"""Unit tests for email verification workflow."""

from __future__ import annotations

import uuid
from datetime import timedelta

import pytest

from core.config.settings import Settings
from core.events.bus import InMemoryEventBus
from database.enums import AuditAction, UserStatus
from authentication.events import EmailVerified
from authentication.exceptions import VerificationException
from authentication.helpers import TokenService, utc_now
from authentication.repositories.memory import MemoryAuthUnitOfWork
from authentication.schemas import EmailVerificationRequest
from authentication.services.email_verification import EmailVerificationService
from authentication.services.providers import MockEmailProvider
from authentication.tests.conftest import make_user, make_verification_token


@pytest.fixture()
def verification_service(
    uow: MemoryAuthUnitOfWork,
    settings: Settings,
    event_bus: InMemoryEventBus,
) -> EmailVerificationService:
    return EmailVerificationService(
        uow_factory=lambda: uow,
        settings=settings,
        email_provider=MockEmailProvider(),
        event_bus=event_bus,
    )


class TestEmailVerification:
    """Email verification token consumption tests."""

    def test_verify_valid_token_sets_email_verified_at(
        self,
        verification_service: EmailVerificationService,
        token_service: TokenService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(
            email="verify@example.com",
            status=UserStatus.PENDING_VERIFICATION,
            email_verified_at=None,
        )
        with uow:
            uow.users.add(user)
        token_pair = token_service.generate()
        with uow:
            uow.tokens.add_email_verification(
                make_verification_token(
                    user_id=user.id,
                    token_hash=token_pair.token_hash,
                    expires_at=utc_now() + timedelta(hours=24),
                )
            )
        verification_service.verify(EmailVerificationRequest(token=token_pair.raw))
        with uow:
            updated = uow.users.get_by_id(user.id)
            assert updated is not None
            assert updated.email_verified_at is not None
            assert updated.status == UserStatus.ACTIVE

    def test_verify_token_updates_status_from_pending_to_active(
        self,
        verification_service: EmailVerificationService,
        token_service: TokenService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(
            email="pending@example.com",
            status=UserStatus.PENDING_VERIFICATION,
            email_verified_at=None,
        )
        with uow:
            uow.users.add(user)
        token_pair = token_service.generate()
        with uow:
            uow.tokens.add_email_verification(
                make_verification_token(
                    user_id=user.id,
                    token_hash=token_pair.token_hash,
                )
            )
        verification_service.verify(EmailVerificationRequest(token=token_pair.raw))
        with uow:
            updated = uow.users.get_by_id(user.id)
            assert updated is not None
            assert updated.status == UserStatus.ACTIVE

    def test_verify_invalid_token_raises_error(
        self,
        verification_service: EmailVerificationService,
    ) -> None:
        with pytest.raises(VerificationException):
            verification_service.verify(
                EmailVerificationRequest(token="invalid-token-that-does-not-exist")
            )

    def test_verify_expired_token_raises_error(
        self,
        verification_service: EmailVerificationService,
        token_service: TokenService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="expired@example.com")
        with uow:
            uow.users.add(user)
        token_pair = token_service.generate()
        with uow:
            uow.tokens.add_email_verification(
                make_verification_token(
                    user_id=user.id,
                    token_hash=token_pair.token_hash,
                    expires_at=utc_now() - timedelta(hours=1),
                )
            )
        with pytest.raises(VerificationException):
            verification_service.verify(EmailVerificationRequest(token=token_pair.raw))

    def test_verify_used_token_raises_error(
        self,
        verification_service: EmailVerificationService,
        token_service: TokenService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="used-token@example.com")
        with uow:
            uow.users.add(user)
        token_pair = token_service.generate()
        with uow:
            token = make_verification_token(
                user_id=user.id,
                token_hash=token_pair.token_hash,
            )
            token.used_at = utc_now()
            uow.tokens.add_email_verification(token)
        with pytest.raises(VerificationException):
            verification_service.verify(EmailVerificationRequest(token=token_pair.raw))

    def test_verify_creates_audit_log(
        self,
        verification_service: EmailVerificationService,
        token_service: TokenService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(
            email="audit-verify@example.com",
            status=UserStatus.PENDING_VERIFICATION,
            email_verified_at=None,
        )
        with uow:
            uow.users.add(user)
        token_pair = token_service.generate()
        with uow:
            uow.tokens.add_email_verification(
                make_verification_token(
                    user_id=user.id,
                    token_hash=token_pair.token_hash,
                )
            )
        verification_service.verify(EmailVerificationRequest(token=token_pair.raw))
        with uow:
            assert any(
                l.action == AuditAction.EMAIL_VERIFICATION
                for l in uow.audit.store.audit_logs
            )

    def test_verify_publishes_event(
        self,
        verification_service: EmailVerificationService,
        token_service: TokenService,
        uow: MemoryAuthUnitOfWork,
        event_bus: InMemoryEventBus,
    ) -> None:
        received: list[EmailVerified] = []
        event_bus.subscribe(EmailVerified, lambda e: received.append(e))
        user = make_user(
            email="event-verify@example.com",
            status=UserStatus.PENDING_VERIFICATION,
            email_verified_at=None,
        )
        with uow:
            uow.users.add(user)
        token_pair = token_service.generate()
        with uow:
            uow.tokens.add_email_verification(
                make_verification_token(
                    user_id=user.id,
                    token_hash=token_pair.token_hash,
                )
            )
        verification_service.verify(EmailVerificationRequest(token=token_pair.raw))
        assert len(received) >= 1

    def test_resend_creates_new_token(
        self,
        verification_service: EmailVerificationService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(
            email="resend@example.com",
            status=UserStatus.PENDING_VERIFICATION,
            email_verified_at=None,
        )
        with uow:
            uow.users.add(user)
        verification_service.resend("resend@example.com")
        with uow:
            tokens = [
                t for t in uow.tokens.store.email_tokens if t.user_id == user.id
            ]
            assert len(tokens) == 1

    def test_resend_for_verified_user_does_nothing(
        self,
        verification_service: EmailVerificationService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="already-verified@example.com")
        with uow:
            uow.users.add(user)
        response = verification_service.resend("already-verified@example.com")
        with uow:
            tokens = [
                t for t in uow.tokens.store.email_tokens if t.user_id == user.id
            ]
            assert len(tokens) == 0
        assert response.accepted is True

    def test_resend_for_nonexistent_user_does_not_reveal(
        self,
        verification_service: EmailVerificationService,
    ) -> None:
        response = verification_service.resend("nobody@example.com")
        assert response.accepted is True
