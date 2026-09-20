"""Account and organization status policies."""

from __future__ import annotations

from datetime import datetime

from authentication.exceptions import (
    AccountLockedException,
    AccountStatusException,
    EmailNotVerifiedException,
    OrganizationStatusException,
)
from database.enums import OrganizationStatus, UserStatus
from database.models.auth import User
from database.models.tenant import Organization


class AccountPolicy:
    """Centralized zero-trust login policy checks."""

    AUTHENTICATABLE_USER_STATUSES = {UserStatus.ACTIVE, UserStatus.PENDING_VERIFICATION}
    BLOCKED_USER_STATUSES = {
        UserStatus.SUSPENDED,
        UserStatus.DISABLED,
        UserStatus.ARCHIVED,
        UserStatus.DELETED,
        UserStatus.INACTIVE,
    }
    AUTHENTICATABLE_ORG_STATUSES = {OrganizationStatus.ACTIVE, OrganizationStatus.TRIAL}

    def assert_user_can_authenticate(self, user: User, *, now: datetime, require_verified_email: bool) -> None:
        if user.deleted_at is not None:
            raise AccountStatusException(details={"status": user.status.value})
        if user.locked_until and user.locked_until > now:
            raise AccountLockedException(details={"locked_until": user.locked_until.isoformat()})
        if user.status in self.BLOCKED_USER_STATUSES:
            raise AccountStatusException(details={"status": user.status.value})
        if require_verified_email and user.email_verified_at is None:
            raise EmailNotVerifiedException()
        if user.password_expires_at and user.password_expires_at <= now:
            raise AccountStatusException("Password has expired.", details={"status": "password_expired"})

    def assert_organization_can_authenticate(self, organization: Organization) -> None:
        if organization.deleted_at is not None or organization.status not in self.AUTHENTICATABLE_ORG_STATUSES:
            raise OrganizationStatusException(details={"status": organization.status.value})
