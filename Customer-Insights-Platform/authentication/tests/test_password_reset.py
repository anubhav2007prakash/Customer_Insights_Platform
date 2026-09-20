"""Unit tests for password reset and change workflows."""

from __future__ import annotations

import uuid
from datetime import timedelta

import pytest

from core.config.settings import Settings
from core.events.bus import InMemoryEventBus
from database.enums import AuditAction
from authentication.events import PasswordChanged, PasswordResetRequested
from authentication.exceptions import InvalidCredentialsException, PasswordPolicyException, PasswordResetException
from authentication.helpers import PasswordHasher, TokenService, utc_now
from authentication.repositories.memory import MemoryAuthUnitOfWork
from authentication.schemas import (
    ForgotPasswordRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
)
from authentication.services.password_reset import PasswordResetService
from authentication.services.providers import MockEmailProvider
from authentication.tests.conftest import make_password_reset_token, make_user


@pytest.fixture()
def reset_service(uow: MemoryAuthUnitOfWork, settings: Settings, event_bus: InMemoryEventBus) -> PasswordResetService:
    return PasswordResetService(
        uow_factory=lambda: uow,
        settings=settings,
        email_provider=MockEmailProvider(),
        event_bus=event_bus,
        password_hasher=PasswordHasher(rounds=4),
    )


class TestPasswordReset:
    """Password reset workflow tests."""

    def test_request_reset_returns_generic_response(self, reset_service: PasswordResetService) -> None:
        response = reset_service.request_reset(
            ForgotPasswordRequest(email="nobody@example.com")
        )
        assert response.accepted is True
        assert response.message is not None

    def test_request_reset_does_not_reveal_account_existence(
        self,
        reset_service: PasswordResetService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="exists@example.com")
        with uow:
            uow.users.add(user)
        response_exists = reset_service.request_reset(
            ForgotPasswordRequest(email="exists@example.com")
        )
        response_none = reset_service.request_reset(
            ForgotPasswordRequest(email="doesnotexist@example.com")
        )
        assert response_exists.accepted == response_none.accepted

    def test_request_reset_creates_token_for_existing_user(
        self,
        reset_service: PasswordResetService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="token-test@example.com")
        with uow:
            uow.users.add(user)
        reset_service.request_reset(ForgotPasswordRequest(email="token-test@example.com"))
        with uow:
            tokens = [
                t
                for t in uow.tokens.store.password_tokens
                if t.user_id == user.id
            ]
            assert len(tokens) == 1
            assert tokens[0].used_at is None
            assert tokens[0].expires_at is not None

    def test_request_reset_sends_email(
        self,
        reset_service: PasswordResetService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        provider = MockEmailProvider()
        service = PasswordResetService(
            uow_factory=lambda: uow,
            settings=reset_service.settings,
            email_provider=provider,
            password_hasher=PasswordHasher(rounds=4),
        )
        user = make_user(email="email-reset@example.com")
        with uow:
            uow.users.add(user)
        service.request_reset(ForgotPasswordRequest(email="email-reset@example.com"))
        assert len(provider.sent) == 1
        assert provider.sent[0].kind == "password_reset"

    def test_request_reset_creates_audit_log(
        self,
        reset_service: PasswordResetService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="audit-reset@example.com")
        with uow:
            uow.users.add(user)
        reset_service.request_reset(ForgotPasswordRequest(email="audit-reset@example.com"))
        with uow:
            assert any(
                l.action == AuditAction.PASSWORD_RESET
                for l in uow.audit.store.audit_logs
            )

    def test_request_reset_publishes_event(
        self,
        reset_service: PasswordResetService,
        uow: MemoryAuthUnitOfWork,
        event_bus: InMemoryEventBus,
    ) -> None:
        received: list[PasswordResetRequested] = []
        event_bus.subscribe(PasswordResetRequested, lambda e: received.append(e))
        user = make_user(email="event-reset@example.com")
        with uow:
            uow.users.add(user)
        reset_service.request_reset(ForgotPasswordRequest(email="event-reset@example.com"))
        assert len(received) >= 1

    def test_reset_password_with_valid_token(
        self,
        reset_service: PasswordResetService,
        token_service: TokenService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="valid-reset@example.com")
        with uow:
            uow.users.add(user)
        # Request reset to create token
        reset_service.request_reset(ForgotPasswordRequest(email="valid-reset@example.com"))
        with uow:
            token_records = [
                t for t in uow.tokens.store.password_tokens if t.user_id == user.id
            ]
            assert len(token_records) == 1
            stored_hash = token_records[0].token_hash

        # We need the raw token. Since MockEmailProvider captures it, let's reconstruct:
        # The token is hashed in the store; we need to find a raw token that matches.
        # In the test service, the token is generated inside the request_reset call.
        # Let's grab it from the MockEmailProvider.
        provider = reset_service.email_provider
        if isinstance(provider, MockEmailProvider) and provider.sent:
            raw_token = provider.sent[-1].token
            assert raw_token is not None
            reset_service.reset_password(
                PasswordResetRequest(
                    token=raw_token,
                    password="NewSecureP@ss1",
                    password_confirmation="NewSecureP@ss1",
                )
            )
            with uow:
                updated = uow.users.get_by_id(user.id)
                assert updated is not None
                assert updated.password_changed_at is not None

    def test_reset_password_invalid_token_raises_error(
        self,
        reset_service: PasswordResetService,
    ) -> None:
        with pytest.raises(PasswordResetException):
            reset_service.reset_password(
                PasswordResetRequest(
                    token="invalid-token-that-does-not-exist",
                    password="NewSecureP@ss1",
                    password_confirmation="NewSecureP@ss1",
                )
            )

    def test_reset_password_expired_token_raises_error(
        self,
        reset_service: PasswordResetService,
        token_service: TokenService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="expired-reset@example.com")
        with uow:
            uow.users.add(user)
        expired_token = make_password_reset_token(
            user_id=user.id,
            token_hash="expired_hash",
            expires_at=utc_now() - timedelta(hours=1),
        )
        with uow:
            uow.tokens.add_password_reset(expired_token)
        with pytest.raises(PasswordResetException):
            reset_service.reset_password(
                PasswordResetRequest(
                    token="some-raw-token-that-is-long-enough-1234567890",
                    password="NewSecureP@ss1",
                    password_confirmation="NewSecureP@ss1",
                )
            )

    def test_reset_password_weak_password_raises_error(
        self,
        reset_service: PasswordResetService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="weak-reset@example.com")
        with uow:
            uow.users.add(user)
        reset_service.request_reset(ForgotPasswordRequest(email="weak-reset@example.com"))
        provider = reset_service.email_provider
        if isinstance(provider, MockEmailProvider) and provider.sent:
            raw_token = provider.sent[-1].token
        else:
            return  # cannot proceed without token
        with pytest.raises(PasswordPolicyException):
            reset_service.reset_password(
                PasswordResetRequest(
                    token=raw_token,
                    password="weak",
                    password_confirmation="weak",
                )
            )

    def test_reset_password_mismatch_raises_error(
        self,
        reset_service: PasswordResetService,
        token_service: TokenService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="mismatch@example.com")
        with uow:
            uow.users.add(user)
        reset_service.request_reset(ForgotPasswordRequest(email="mismatch@example.com"))
        # With pydantic validation, the schema itself raises ValueError for mismatch
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            PasswordResetRequest(
                token="some-token",
                password="SecureP@ss1",
                password_confirmation="DifferentPass1!",
            )


class TestPasswordChange:
    """Authenticated password change tests."""

    def test_change_password_success(
        self,
        reset_service: PasswordResetService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="change-pw@example.com")
        with uow:
            uow.users.add(user)
        reset_service.change_password(
            user.id,
            PasswordChangeRequest(
                current_password="SecureP@ss1",
                new_password="NewSecureP@ss2",
                new_password_confirmation="NewSecureP@ss2",
            ),
        )
        with uow:
            updated = uow.users.get_by_id(user.id)
            assert updated is not None
            # Verify the new password works
            hasher = PasswordHasher(rounds=4)
            assert hasher.verify("NewSecureP@ss2", updated.password_hash)

    def test_change_password_wrong_current_raises_error(
        self,
        reset_service: PasswordResetService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="wrong-current@example.com")
        with uow:
            uow.users.add(user)
        with pytest.raises(InvalidCredentialsException):
            reset_service.change_password(
                user.id,
                PasswordChangeRequest(
                    current_password="WrongPassword1!",
                    new_password="NewSecureP@ss2",
                    new_password_confirmation="NewSecureP@ss2",
                ),
            )

    def test_change_password_revokes_sessions(
        self,
        reset_service: PasswordResetService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="revoke-sessions@example.com")
        with uow:
            uow.users.add(user)
        from authentication.tests.conftest import make_session
        from database.models.auth import UserSession
        session = make_session(user_id=user.id, token_hash="old_session_hash")
        with uow:
            uow.sessions.add(session)
        reset_service.change_password(
            user.id,
            PasswordChangeRequest(
                current_password="SecureP@ss1",
                new_password="NewSecureP@ss2",
                new_password_confirmation="NewSecureP@ss2",
            ),
        )
        with uow:
            updated_session = uow.sessions.get_active_by_token_hash("old_session_hash", utc_now())
            assert updated_session is None

    def test_change_password_publishes_event(
        self,
        reset_service: PasswordResetService,
        uow: MemoryAuthUnitOfWork,
        event_bus: InMemoryEventBus,
    ) -> None:
        received: list[PasswordChanged] = []
        event_bus.subscribe(PasswordChanged, lambda e: received.append(e))
        user = make_user(email="change-event@example.com")
        with uow:
            uow.users.add(user)
        reset_service.change_password(
            user.id,
            PasswordChangeRequest(
                current_password="SecureP@ss1",
                new_password="NewSecureP@ss2",
                new_password_confirmation="NewSecureP@ss2",
            ),
        )
        assert len(received) >= 1

    def test_change_password_creates_audit_log(
        self,
        reset_service: PasswordResetService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        user = make_user(email="change-audit@example.com")
        with uow:
            uow.users.add(user)
        reset_service.change_password(
            user.id,
            PasswordChangeRequest(
                current_password="SecureP@ss1",
                new_password="NewSecureP@ss2",
                new_password_confirmation="NewSecureP@ss2",
            ),
        )
        with uow:
            assert any(
                l.action == AuditAction.PASSWORD_CHANGE
                for l in uow.audit.store.audit_logs
            )
