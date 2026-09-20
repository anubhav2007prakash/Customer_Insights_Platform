"""Unit tests for account policy enforcement."""

from __future__ import annotations

from datetime import timedelta

import pytest

from core.config.settings import SecuritySettings, Settings
from database.enums import OrganizationStatus, UserStatus
from database.models.auth import User
from database.models.tenant import Organization
from authentication.exceptions import (
    AccountLockedException,
    AccountStatusException,
    EmailNotVerifiedException,
    OrganizationStatusException,
)
from authentication.helpers import utc_now
from authentication.policies import AccountPolicy
from authentication.tests.conftest import make_organization, make_user


class TestAccountPolicy:
    """Account status authorization tests."""

    def test_active_user_can_authenticate(self) -> None:
        policy = AccountPolicy()
        user = make_user(status=UserStatus.ACTIVE)
        policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=True)

    def test_locked_user_cannot_authenticate(self) -> None:
        policy = AccountPolicy()
        user = make_user(
            status=UserStatus.LOCKED,
            locked_until=utc_now() + timedelta(minutes=15),
        )
        with pytest.raises(AccountLockedException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=True)

    def test_unverified_email_raises_error(self) -> None:
        policy = AccountPolicy()
        user = make_user(
            status=UserStatus.PENDING_VERIFICATION,
            email_verified_at=None,
        )
        with pytest.raises(EmailNotVerifiedException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=True)

    def test_unverified_email_allowed_when_not_required(self) -> None:
        policy = AccountPolicy()
        user = make_user(
            status=UserStatus.PENDING_VERIFICATION,
            email_verified_at=None,
        )
        # Should not raise when require_verified_email=False
        policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=False)

    def test_suspended_user_cannot_authenticate(self) -> None:
        policy = AccountPolicy()
        user = make_user(status=UserStatus.SUSPENDED)
        with pytest.raises(AccountStatusException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=True)

    def test_disabled_user_cannot_authenticate(self) -> None:
        policy = AccountPolicy()
        user = make_user(status=UserStatus.DISABLED)
        with pytest.raises(AccountStatusException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=True)

    def test_archived_user_cannot_authenticate(self) -> None:
        policy = AccountPolicy()
        user = make_user(status=UserStatus.ARCHIVED)
        with pytest.raises(AccountStatusException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=True)

    def test_deleted_user_cannot_authenticate(self) -> None:
        policy = AccountPolicy()
        user = make_user(status=UserStatus.DELETED)
        with pytest.raises(AccountStatusException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=True)

    def test_soft_deleted_user_cannot_authenticate(self) -> None:
        from datetime import datetime, timezone
        policy = AccountPolicy()
        user = make_user(status=UserStatus.ACTIVE)
        user.deleted_at = datetime.now(timezone.utc)
        with pytest.raises(AccountStatusException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=True)

    def test_password_expired_raises_error(self) -> None:
        policy = AccountPolicy()
        user = make_user(status=UserStatus.ACTIVE)
        user.password_expires_at = utc_now() - timedelta(days=1)
        with pytest.raises(AccountStatusException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=True)

    def test_active_org_can_authenticate(self) -> None:
        policy = AccountPolicy()
        org = make_organization(status=OrganizationStatus.ACTIVE)
        policy.assert_organization_can_authenticate(org)

    def test_trial_org_can_authenticate(self) -> None:
        policy = AccountPolicy()
        org = make_organization(status=OrganizationStatus.TRIAL)
        policy.assert_organization_can_authenticate(org)

    def test_suspended_org_cannot_authenticate(self) -> None:
        policy = AccountPolicy()
        org = make_organization(status=OrganizationStatus.SUSPENDED)
        with pytest.raises(OrganizationStatusException):
            policy.assert_organization_can_authenticate(org)

    def test_disabled_org_cannot_authenticate(self) -> None:
        policy = AccountPolicy()
        org = make_organization(status=OrganizationStatus.DISABLED)
        with pytest.raises(OrganizationStatusException):
            policy.assert_organization_can_authenticate(org)

    def test_deleted_org_cannot_authenticate(self) -> None:
        from datetime import datetime, timezone
        policy = AccountPolicy()
        org = make_organization(status=OrganizationStatus.ACTIVE)
        org.deleted_at = datetime.now(timezone.utc)
        with pytest.raises(OrganizationStatusException):
            policy.assert_organization_can_authenticate(org)
