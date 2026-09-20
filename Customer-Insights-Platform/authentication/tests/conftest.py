"""Shared fixtures for authentication tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pytest import FixtureRequest

from core.config.settings import SecuritySettings, Settings
from core.events.bus import InMemoryEventBus
from core.exceptions.base import InsightForgeError
from database.enums import OrganizationStatus, UserStatus
from database.models.auth import (
    EmailVerificationToken,
    NotificationSetting,
    PasswordHistory,
    PasswordResetToken,
    User,
    UserPreference,
    UserProfile,
    UserSession,
)
from database.models.notifications import Notification
from database.models.security import AuditLog, SecurityEvent
from database.models.tenant import Organization, OrganizationMember, Role, UserRole, Workspace
from authentication.helpers import PasswordHasher, TokenService, utc_now
from authentication.repositories.memory import MemoryAuthStore, MemoryAuthUnitOfWork

# ---------------------------------------------------------------------------
# Test configuration
# ---------------------------------------------------------------------------

TEST_SECRET_KEY = "test-secret-key-not-for-production"
TEST_PASSWORD = "SecureP@ss1"
TEST_HASHED_PASSWORD: str | None = None


def _hash_password() -> str:
    global TEST_HASHED_PASSWORD
    if TEST_HASHED_PASSWORD is None:
        TEST_HASHED_PASSWORD = PasswordHasher(rounds=4).hash(TEST_PASSWORD)
    return TEST_HASHED_PASSWORD


@pytest.fixture(scope="function", autouse=True)
def _reset_memory_store() -> None:
    MemoryAuthUnitOfWork.reset_store()


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

@pytest.fixture()
def security_settings() -> SecuritySettings:
    return SecuritySettings(
        secret_key=TEST_SECRET_KEY,
        password_min_length=8,
        password_max_length=128,
        password_require_uppercase=True,
        password_require_lowercase=True,
        password_require_numeric=True,
        password_require_special=True,
        password_history_count=5,
        password_expiration_days=90,
        bcrypt_rounds=4,  # fast for tests
        session_ttl_hours=24,
        remember_me_ttl_days=30,
        max_login_attempts=5,
        lockout_minutes=15,
        email_verification_token_ttl_hours=24,
        password_reset_token_ttl_minutes=30,
        username_unique=True,
        require_verified_email=True,
    )


@pytest.fixture()
def settings(security_settings: SecuritySettings) -> Settings:
    return Settings(security=security_settings, debug=True)


# ---------------------------------------------------------------------------
# In-memory store & unit-of-work
# ---------------------------------------------------------------------------

@pytest.fixture()
def auth_store() -> MemoryAuthStore:
    return MemoryAuthStore()


@pytest.fixture()
def uow(auth_store: MemoryAuthStore) -> MemoryAuthUnitOfWork:
    return MemoryAuthUnitOfWork(store=auth_store)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

@pytest.fixture()
def password_hasher() -> PasswordHasher:
    return PasswordHasher(rounds=4)


@pytest.fixture()
def token_service(settings: Settings) -> TokenService:
    return TokenService(settings.security.secret_key)


@pytest.fixture()
def event_bus() -> InMemoryEventBus:
    return InMemoryEventBus()


# ---------------------------------------------------------------------------
# Common data
# ---------------------------------------------------------------------------

def make_user(
    *,
    email: str = "test@example.com",
    username: str | None = "testuser",
    password_hash: str | None = None,
    status: UserStatus = UserStatus.ACTIVE,
    email_verified_at: datetime | None = None,
    locked_until: datetime | None = None,
    failed_login_attempts: int = 0,
) -> User:
    now = utc_now()
    if email_verified_at is None and status == UserStatus.ACTIVE:
        email_verified_at = now
    return User(
        id=uuid.uuid4(),
        email=email,
        username=username,
        password_hash=password_hash or _hash_password(),
        status=status,
        email_verified_at=email_verified_at,
        password_changed_at=now,
        password_expires_at=now + timedelta(days=90),
        failed_login_attempts=failed_login_attempts,
        locked_until=locked_until,
        last_login_at=None,
    )


def make_organization(
    *,
    name: str = "Test Corp",
    slug: str = "test-corp",
    status: OrganizationStatus = OrganizationStatus.ACTIVE,
) -> Organization:
    return Organization(
        id=uuid.uuid4(),
        name=name,
        slug=slug,
        status=status,
        timezone="UTC",
        locale="en-US",
    )


def make_session(
    *,
    user_id: uuid.UUID,
    organization_id: uuid.UUID | None = None,
    token_hash: str = "valid_hash",
    expires_at: datetime | None = None,
) -> UserSession:
    now = utc_now()
    return UserSession(
        id=uuid.uuid4(),
        user_id=user_id,
        organization_id=organization_id,
        token_hash=token_hash,
        device_fingerprint=None,
        device_name=None,
        remember_me=False,
        ip_address=None,
        user_agent=None,
        last_seen_at=now,
        expires_at=expires_at or (now + timedelta(hours=24)),
        revoked_at=None,
    )


def make_verification_token(
    *,
    user_id: uuid.UUID,
    email: str = "test@example.com",
    token_hash: str = "valid_vtoken_hash",
    expires_at: datetime | None = None,
) -> EmailVerificationToken:
    return EmailVerificationToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=token_hash,
        email=email,
        expires_at=expires_at or (utc_now() + timedelta(hours=24)),
        used_at=None,
    )


def make_password_reset_token(
    *,
    user_id: uuid.UUID,
    token_hash: str = "valid_ptoken_hash",
    expires_at: datetime | None = None,
) -> PasswordResetToken:
    return PasswordResetToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at or (utc_now() + timedelta(hours=24)),
        used_at=None,
        requested_ip=None,
        user_agent=None,
    )


@pytest.fixture()
def seed_user(uow: MemoryAuthUnitOfWork) -> User:
    user = make_user()
    with uow:
        uow.users.add(user)
        uow.users.add_profile(
            UserProfile(
                id=uuid.uuid4(),
                user_id=user.id,
                first_name="Test",
                last_name="User",
                display_name="Test User",
                timezone="UTC",
                language="en",
                locale="en-US",
                notification_settings={},
                profile_completion=60,
            )
        )
    return user


@pytest.fixture()
def seed_org(uow: MemoryAuthUnitOfWork) -> Organization:
    org = make_organization()
    with uow:
        uow.organizations.add(org)
    return org


@pytest.fixture()
def seed_org_with_user(seed_org: Organization, seed_user: User, uow: MemoryAuthUnitOfWork) -> tuple[Organization, User]:
    with uow:
        uow.organizations.add_member(
            OrganizationMember(
                id=uuid.uuid4(),
                organization_id=seed_org.id,
                user_id=seed_user.id,
                role_id=None,
                is_owner=True,
                joined_at=utc_now(),
            )
        )
    return seed_org, seed_user
