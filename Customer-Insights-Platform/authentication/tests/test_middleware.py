"""Unit tests for authentication middleware."""

from __future__ import annotations

import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest

from core.config.settings import Settings
from core.exceptions.base import SessionExpiredError
from authentication.helpers import TokenService, utc_now
from authentication.middleware import AuthenticatedContext, SessionMiddleware
from authentication.repositories.memory import MemoryAuthUnitOfWork
from authentication.services.sessions import SessionService
from authentication.tests.conftest import make_session, make_user


class TestSessionMiddleware:
    """Token validation middleware tests."""

    def test_authenticate_valid_token_returns_context(
        self,
        uow: MemoryAuthUnitOfWork,
        settings: Settings,
    ) -> None:
        ts = TokenService(settings.security.secret_key)
        token_pair = ts.generate()
        user = make_user(email="mid-test@example.com")
        session = make_session(
            user_id=user.id,
            organization_id=None,
            token_hash=token_pair.token_hash,
        )
        with uow:
            uow.users.add(user)
            uow.sessions.add(session)

        session_service = SessionService(uow_factory=lambda: uow, settings=settings)
        middleware = SessionMiddleware(session_service=session_service)
        ctx = middleware.authenticate_token(token_pair.raw)
        assert isinstance(ctx, AuthenticatedContext)
        assert ctx.user_id == user.id
        assert ctx.session_id == session.id
        assert ctx.organization_id is None

    def test_authenticate_invalid_token_raises_error(
        self,
        uow: MemoryAuthUnitOfWork,
        settings: Settings,
    ) -> None:
        session_service = SessionService(uow_factory=lambda: uow, settings=settings)
        middleware = SessionMiddleware(session_service=session_service)
        with pytest.raises(SessionExpiredError):
            middleware.authenticate_token("invalid-token")

    def test_authenticate_expired_session_raises_error(
        self,
        uow: MemoryAuthUnitOfWork,
        settings: Settings,
    ) -> None:
        ts = TokenService(settings.security.secret_key)
        token_pair = ts.generate()
        user = make_user(email="expired-mid@example.com")
        session = make_session(
            user_id=user.id,
            token_hash=token_pair.token_hash,
            expires_at=utc_now() - timedelta(hours=1),
        )
        with uow:
            uow.users.add(user)
            uow.sessions.add(session)

        session_service = SessionService(uow_factory=lambda: uow, settings=settings)
        middleware = SessionMiddleware(session_service=session_service)
        with pytest.raises(SessionExpiredError):
            middleware.authenticate_token(token_pair.raw)

    def test_authenticate_revoked_session_raises_error(
        self,
        uow: MemoryAuthUnitOfWork,
        settings: Settings,
    ) -> None:
        ts = TokenService(settings.security.secret_key)
        token_pair = ts.generate()
        user = make_user(email="revoked-mid@example.com")
        session = make_session(
            user_id=user.id,
            token_hash=token_pair.token_hash,
        )
        session.revoked_at = utc_now()
        with uow:
            uow.users.add(user)
            uow.sessions.add(session)

        session_service = SessionService(uow_factory=lambda: uow, settings=settings)
        middleware = SessionMiddleware(session_service=session_service)
        with pytest.raises(SessionExpiredError):
            middleware.authenticate_token(token_pair.raw)
