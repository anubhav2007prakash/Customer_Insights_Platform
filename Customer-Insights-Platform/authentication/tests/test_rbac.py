"""Unit tests for RBAC (Role-Based Access Control)."""

from __future__ import annotations

import pytest

from authentication.permissions import AuthPermission, RBACService
from core.exceptions.base import AuthorizationError


class TestRBACService:
    """Permission checking tests."""

    def test_has_permission_returns_true(self) -> None:
        rbac = RBACService()
        assert rbac.has_permission({"users.read"}, "users.read") is True

    def test_has_permission_returns_false(self) -> None:
        rbac = RBACService()
        assert rbac.has_permission({"customers.read"}, "users.read") is False

    def test_has_permission_admin_full(self) -> None:
        rbac = RBACService()
        assert rbac.has_permission({"admin.full"}, "users.read") is True
        assert rbac.has_permission({"admin.full"}, "settings.manage") is True

    def test_has_permission_empty_set(self) -> None:
        rbac = RBACService()
        assert rbac.has_permission(set(), "users.read") is False

    def test_require_passes_for_valid_permission(self) -> None:
        rbac = RBACService()
        rbac.require({"users.read", "users.write"}, "users.read")

    def test_require_raises_for_missing_permission(self) -> None:
        rbac = RBACService()
        with pytest.raises(AuthorizationError):
            rbac.require({"customers.read"}, "users.write")

    def test_require_admin_full_passes_all(self) -> None:
        rbac = RBACService()
        rbac.require({"admin.full"}, "anything.here")

    def test_frozenset_permissions(self) -> None:
        rbac = RBACService()
        perms = frozenset({"users.read", "users.write"})
        assert rbac.has_permission(perms, "users.write") is True
        assert rbac.has_permission(perms, "roles.manage") is False

    def test_require_with_frozenset(self) -> None:
        rbac = RBACService()
        rbac.require(frozenset({"users.read"}), "users.read")


class TestAuthPermission:
    """AuthPermission enum tests."""

    def test_enum_values(self) -> None:
        assert AuthPermission.USERS_READ == "users.read"
        assert AuthPermission.USERS_WRITE == "users.write"
        assert AuthPermission.ROLES_MANAGE == "roles.manage"
        assert AuthPermission.SETTINGS_MANAGE == "settings.manage"
        assert AuthPermission.ADMIN_FULL == "admin.full"

    def test_enum_membership(self) -> None:
        assert "users.read" in AuthPermission.__members__.values()
