"""Unit tests for authentication decorators."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from authentication.decorators import require_authenticated_session, require_permission
from core.exceptions.base import AuthenticationError, AuthorizationError


class TestRequireAuthenticatedSession:
    """Session requirement decorator tests."""

    def test_passes_with_session_in_kwargs(self) -> None:
        @require_authenticated_session
        def handler(*, session: object) -> str:
            return "ok"

        result = handler(session=MagicMock(user_id="user-1"))
        assert result == "ok"

    def test_passes_with_session_as_second_arg(self) -> None:
        @require_authenticated_session
        def handler(self, session: object) -> str:  # type: ignore[no-untyped-def]
            return "ok"

        result = handler(None, MagicMock(user_id="user-1"))
        assert result == "ok"

    def test_raises_without_session(self) -> None:
        @require_authenticated_session
        def handler(*, session: object = None) -> str:  # type: ignore[assignment]
            return "ok"

        with pytest.raises(AuthenticationError):
            handler(session=None)

    def test_raises_without_user_id(self) -> None:
        @require_authenticated_session
        def handler(*, session: object) -> str:
            return "ok"

        with pytest.raises(AuthenticationError):
            handler(session=MagicMock(user_id=None))


class TestRequirePermission:
    """Permission requirement decorator tests."""

    def test_passes_with_permission_in_kwargs(self) -> None:
        @require_permission("users.read")
        def handler(*, permissions: set[str] = None) -> str:  # type: ignore[assignment]
            return "ok"

        result = handler(permissions={"users.read"})
        assert result == "ok"

    def test_raises_without_permission(self) -> None:
        @require_permission("users.write")
        def handler(*, permissions: set[str] = None) -> str:  # type: ignore[assignment]
            return "ok"

        with pytest.raises(AuthorizationError):
            handler(permissions={"users.read"})

    def test_passes_with_admin_full(self) -> None:
        @require_permission("any.permission")
        def handler(*, permissions: set[str] = None) -> str:  # type: ignore[assignment]
            return "ok"

        result = handler(permissions={"admin.full"})
        assert result == "ok"

    def test_raises_without_permissions_arg(self) -> None:
        @require_permission("users.read")
        def handler(*, permissions: object = None) -> str:
            return "ok"

        with pytest.raises(AuthenticationError):
            handler(permissions=None)

    def test_permissions_from_second_arg_attr(self) -> None:
        @require_permission("users.read")
        def handler(self, ctx: object) -> str:  # type: ignore[no-untyped-def]
            return "ok"

        ctx = MagicMock(permissions={"users.read"})
        result = handler(None, ctx)
        assert result == "ok"
