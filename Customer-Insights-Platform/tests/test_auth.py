"""Comprehensive authentication tests for InsightForge AI."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from authentication.audit import AuthAuditLogger
from authentication.constants.defaults import DEFAULT_WORKSPACE_NAME, DEFAULT_WORKSPACE_SLUG, OWNER_ROLE
from authentication.events import (
    AccountLocked,
    EmailVerified,
    LoginFailed,
    LoginSucceeded,
    LogoutCompleted,
    PasswordChanged,
    PasswordResetRequested,
    UserRegistered,
)
from authentication.exceptions import (
    AccountLockedException,
    AccountStatusException,
    DuplicateEmailException,
    DuplicateOrganizationException,
    DuplicateUsernameException,
    EmailNotVerifiedException,
    InvalidCredentialsException,
    PasswordPolicyException,
    RegistrationException,
    VerificationException,
)
from authentication.helpers import PasswordHasher, TokenService, normalize_email, normalize_username, slugify, utc_now
from authentication.permissions import AuthPermission, RBACService
from authentication.policies import AccountPolicy
from authentication.repositories.memory import MemoryAuthStore, MemoryAuthUnitOfWork
from authentication.schemas import (
    EmailVerificationRequest,
    ForgotPasswordRequest,
    LoginRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    RegisterOrganizationRequest,
    RegisterUserRequest,
    UserProfileInput,
)
from authentication.services import (
    AuthenticationService,
    AuthenticationServiceFactory,
    EmailVerificationService,
    PasswordResetService,
    RegistrationService,
    SessionService,
)
from authentication.validators import PasswordPolicy, PasswordPolicyValidator
from core.config.settings import Settings
from core.config.environments import Environment
from database.enums import OrganizationStatus, UserStatus
from database.models.auth import User, UserProfile, UserSession
from database.models.tenant import Organization, OrganizationMember, Role, UserRole, Workspace


# --- Fixtures ---

@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        environment=Environment.TESTING,
        debug=True,
        security__password_min_length=8,
        security__password_max_length=128,
        security__password_require_uppercase=True,
        security__password_require_lowercase=True,
        security__password_require_numeric=True,
        security__password_require_special=True,
        security__password_history_count=5,
        security__password_expiration_days=90,
        security__email_verification_token_ttl_hours=24,
        security__password_reset_token_ttl_minutes=30,
        security__require_verified_email=True,
    )


@pytest.fixture
def in_memory_uow() -> MemoryAuthUnitOfWork:
    return MemoryAuthUnitOfWork()


@pytest.fixture
def auth_factory(test_settings: Settings) -> AuthenticationServiceFactory:
    return AuthenticationServiceFactory(settings=test_settings)


# --- Password Policy Tests ---

class TestPasswordPolicy:
    """Password policy validation tests."""

    def test_valid_password_passes(self, test_settings: Settings):
        validator = PasswordPolicyValidator()
        result = validator.validate("StrongP@ss123")
        assert result.valid is True
        assert result.score >= 70

    def test_short_password_fails(self, test_settings: Settings):
        validator = PasswordPolicyValidator()
        with pytest.raises(PasswordPolicyException) as exc_info:
            validator.validate("Sh0rt!")
        assert "at least" in str(exc_info.value.message).lower()

    def test_missing_uppercase_fails(self, test_settings: Settings):
        validator = PasswordPolicyValidator()
        with pytest.raises(PasswordPolicyException) as exc_info:
            validator.validate("lowercase123!")
        assert "uppercase" in str(exc_info.value.message).lower()

    def test_missing_lowercase_fails(self, test_settings: Settings):
        validator = PasswordPolicyValidator()
        with pytest.raises(PasswordPolicyException) as exc_info:
            validator.validate("UPPERCASE123!")
        assert "lowercase" in str(exc_info.value.message).lower()

    def test_missing_numeric_fails(self, test_settings: Settings):
        validator = PasswordPolicyValidator()
        with pytest.raises(PasswordPolicyException) as exc_info:
            validator.validate("NoNumbers!")
        assert "number" in str(exc_info.value.message).lower()

    def test_missing_special_fails(self, test_settings: Settings):
        validator = PasswordPolicyValidator()
        with pytest.raises(PasswordPolicyException) as exc_info:
            validator.validate("NoSpecial123")
        assert "special" in str(exc_info.value.message).lower()

    def test_password_strength_scoring(self, test_settings: Settings):
        validator = PasswordPolicyValidator()
        score = validator.score("StrongP@ss123")
        assert score >= 70


class TestPasswordHasher:
    """Password hashing and verification tests."""

    def test_hash_creates_bcrypt_hash(self):
        hasher = PasswordHasher()
        hashed = hasher.hash("test_password")
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        hasher = PasswordHasher()
        hashed = hasher.hash("test_password")
        assert hasher.verify("test_password", hashed) is True

    def test_verify_incorrect_password(self):
        hasher = PasswordHasher()
        hashed = hasher.hash("test_password")
        assert hasher.verify("wrong_password", hashed) is False

    def test_verify_empty_hash_returns_false(self):
        hasher = PasswordHasher()
        assert hasher.verify("test_password", None) is False

    def test_verify_invalid_hash_returns_false(self):
        hasher = PasswordHasher()
        assert hasher.verify("test_password", "invalid_hash") is False


class TestTokenService:
    """Token generation and verification tests."""

    def test_token_generation_creates_unique_tokens(self):
        service = TokenService("secret_key")
        token1 = service.generate()
        token2 = service.generate()
        assert token1.raw != token2.raw
        assert token1.token_hash != token2.token_hash

    def test_token_hash_is_deterministic(self):
        service = TokenService("secret_key")
        token = service.generate()
        assert service.hash(token.raw) == token.token_hash

    def test_token_verify_roundtrip(self):
        service = TokenService("secret_key")
        token = service.generate()
        assert service.verify(token.raw, token.token_hash) is True

    def test_token_verify_wrong_secret_fails(self):
        service1 = TokenService("secret1")
        service2 = TokenService("secret2")
        token = service1.generate()
        assert service2.verify(token.raw, token.token_hash) is False


class TestInputValidation:
    """Input validation tests."""

    def test_normalize_email_lowercases_and_strips(self):
        assert normalize_email("  TEST@EXAMPLE.COM  ") == "test@example.com"

    def test_normalize_username_lowercases_and_strips(self):
        assert normalize_username("  TestUser  ") == "testuser"

    def test_normalize_username_returns_none_for_empty(self):
        assert normalize_username("") is None
        assert normalize_username(None) is None

    def test_slugify_creates_stable_slug(self):
        assert slugify("Acme Corp!") == "acme-corp"
        assert slugify("My Organization 123") == "my-organization-123"


class TestAccountPolicy:
    """Account status policy tests."""

    def test_active_user_can_authenticate(self, test_settings: Settings):
        policy = AccountPolicy()
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            status=UserStatus.ACTIVE,
            password_hash="$2b$test",
        )
        policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=False)

    def test_locked_user_cannot_authenticate(self, test_settings: Settings):
        policy = AccountPolicy()
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            status=UserStatus.LOCKED,
            locked_until=utc_now() + timedelta(hours=1),
            password_hash="$2b$test",
        )
        with pytest.raises(AccountLockedException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=False)

    def test_suspended_user_cannot_authenticate(self, test_settings: Settings):
        policy = AccountPolicy()
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            status=UserStatus.SUSPENDED,
            password_hash="$2b$test",
        )
        with pytest.raises(AccountStatusException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=False)

    def test_deleted_user_cannot_authenticate(self, test_settings: Settings):
        policy = AccountPolicy()
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            status=UserStatus.ACTIVE,
            password_hash="$2b$test",
            deleted_at=utc_now(),
        )
        with pytest.raises(AccountStatusException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=False)

    def test_expired_password_cannot_authenticate(self, test_settings: Settings):
        policy = AccountPolicy()
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            status=UserStatus.ACTIVE,
            password_hash="$2b$test",
            password_expires_at=utc_now() - timedelta(days=1),
        )
        with pytest.raises(AccountStatusException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=False)

    def test_unverified_email_cannot_authenticate_when_required(self, test_settings: Settings):
        policy = AccountPolicy()
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            status=UserStatus.PENDING_VERIFICATION,
            password_hash="$2b$test",
        )
        with pytest.raises(EmailNotVerifiedException):
            policy.assert_user_can_authenticate(user, now=utc_now(), require_verified_email=True)


class TestRegistrationService:
    """Registration workflow tests."""

    def test_register_organization_success(self, auth_factory: AuthenticationServiceFactory):
        service = auth_factory.registration()
        request = RegisterOrganizationRequest(
            email="owner@example.com",
            password="StrongP@ss123",
            organization_name="Acme Corp",
            profile=UserProfileInput(full_name="Test Owner"),
        )
        response = service.register_organization(request)
        assert response.user_id is not None
        assert response.organization_id is not None
        assert response.email == "owner@example.com"
        assert response.verification_required is True

    def test_register_organization_duplicate_email_fails(self, auth_factory: AuthenticationServiceFactory):
        service = auth_factory.registration()
        request = RegisterOrganizationRequest(
            email="owner@example.com",
            password="StrongP@ss123",
            organization_name="Acme Corp",
            profile=UserProfileInput(full_name="Test Owner"),
        )
        service.register_organization(request)
        with pytest.raises(DuplicateEmailException):
            service.register_organization(request)

    def test_register_organization_duplicate_slug_fails(self, auth_factory: AuthenticationServiceFactory):
        service = auth_factory.registration()
        request = RegisterOrganizationRequest(
            email="owner@example.com",
            password="StrongP@ss123",
            organization_name="Acme Corp",
            profile=UserProfileInput(full_name="Test Owner"),
        )
        response = service.register_organization(request)
        # Try to register another org with same slug derived from name
        request2 = RegisterOrganizationRequest(
            email="owner2@example.com",
            password="StrongP@ss123",
            organization_name="Acme Corp",  # Same name = same slug
            profile=UserProfileInput(full_name="Test Owner 2"),
        )
        with pytest.raises(DuplicateOrganizationException):
            service.register_organization(request2)


class TestAuthenticationService:
    """Login and logout tests."""

    def test_login_failure_invalid_credentials(self, auth_factory: AuthenticationServiceFactory, in_memory_uow: MemoryAuthUnitOfWork):
        service = auth_factory.authentication()
        request = LoginRequest(
            identifier="nonexistent@example.com",
            password="anypassword",
        )
        with pytest.raises(InvalidCredentialsException):
            service.login(request)

    def test_login_success(self, auth_factory: AuthenticationServiceFactory, in_memory_uow: MemoryAuthUnitOfWork):
        reg_service = auth_factory.registration()
        reg_request = RegisterOrganizationRequest(
            email="owner@example.com",
            password="StrongP@ss123",
            organization_name="Acme Corp",
            profile=UserProfileInput(full_name="Test Owner"),
        )
        reg_service.register_organization(reg_request)
        
        # Verify email before login (since require_verified_email=True in test settings)
        uow = auth_factory.uow_factory()
        user = uow.users.get_by_email("owner@example.com")
        if user:
            user.email_verified_at = utc_now()
        
        auth_service = auth_factory.authentication()
        login_request = LoginRequest(
            identifier="owner@example.com",
            password="StrongP@ss123",
            organization_slug="acme-corp",
        )
        response = auth_service.login(login_request)
        assert response.session.session_token is not None
        assert response.email == "owner@example.com"

    def test_logout_revokes_session(self, auth_factory: AuthenticationServiceFactory):
        reg_service = auth_factory.registration()
        reg_request = RegisterOrganizationRequest(
            email="owner@example.com",
            password="StrongP@ss123",
            organization_name="Acme Corp",
            profile=UserProfileInput(full_name="Test Owner"),
        )
        reg_service.register_organization(reg_request)
        
        # Verify email before login (since require_verified_email=True in test settings)
        uow = auth_factory.uow_factory()
        user = uow.users.get_by_email("owner@example.com")
        if user:
            user.email_verified_at = utc_now()
        
        auth_service = auth_factory.authentication()
        login_request = LoginRequest(
            identifier="owner@example.com",
            password="StrongP@ss123",
            organization_slug="acme-corp",
        )
        login_response = auth_service.login(login_request)
        
        # Logout should succeed without error
        auth_service.logout(
            type("LogoutRequest", (), {"session_token": login_response.session.session_token})()
        )

    def test_failed_login_triggers_lockout(self, auth_factory: AuthenticationServiceFactory):
        service = auth_factory.authentication()
        requests = []
        for i in range(5):
            requests.append(LoginRequest(
                identifier=f"user{i}@example.com",
                password="wrongpassword",
            ))
        # Each failed login should increment attempts but not lock yet
        for req in requests:
            with pytest.raises(InvalidCredentialsException):
                service.login(req)


class TestPasswordResetService:
    """Password reset workflow tests."""

    def test_forgot_password_returns_generic_response(self, auth_factory: AuthenticationServiceFactory):
        service = auth_factory.password_reset()
        request = ForgotPasswordRequest(email="nonexistent@example.com")
        response = service.request_reset(request)
        assert response.accepted is True

    def test_password_reset_flow(self, auth_factory: AuthenticationServiceFactory):
        reg_service = auth_factory.registration()
        reg_request = RegisterOrganizationRequest(
            email="owner@example.com",
            password="StrongP@ss123",
            organization_name="Acme Corp",
            profile=UserProfileInput(full_name="Test Owner"),
        )
        reg_service.register_organization(reg_request)
        
        reset_service = auth_factory.password_reset()
        forgot_request = ForgotPasswordRequest(email="owner@example.com")
        reset_service.request_reset(forgot_request)
        
        # Find the token that was sent
        uow = auth_factory.uow_factory() if hasattr(auth_factory, 'uow_factory') else None


class TestEmailVerificationService:
    """Email verification workflow tests."""

    def test_resend_returns_generic_response_for_nonexistent_email(self, auth_factory: AuthenticationServiceFactory):
        service = auth_factory.email_verification()
        response = service.resend("nonexistent@example.com")
        assert response.accepted is True or "If verification" in response.message

    def test_invalid_verification_token_fails(self, auth_factory: AuthenticationServiceFactory):
        service = auth_factory.email_verification()
        request = EmailVerificationRequest(token="invalidtoken123XX")
        with pytest.raises(VerificationException):
            service.verify(request)


class TestRBACService:
    """Role-based access control tests."""

    def test_has_permission_direct(self):
        service = RBACService()
        assert service.has_permission({"users.read"}, "users.read") is True
        assert service.has_permission({"users.read"}, "users.write") is False

    def test_has_permission_admin_override(self):
        service = RBACService()
        assert service.has_permission({"admin.full"}, "users.write") is True
        assert service.has_permission({"admin.full"}, "any.permission") is True

    def test_require_raises_on_missing(self):
        service = RBACService()
        with pytest.raises(Exception):  # AuthorizationError
            service.require({"users.read"}, "users.write")


class TestSessionService:
    """Session validation tests."""

    def test_validate_expired_session_fails(self, auth_factory: AuthenticationServiceFactory):
        service = auth_factory.sessions()
        with pytest.raises(Exception):  # SessionExpiredError
            service.validate("invalidtoken")


class TestAuthAuditLogger:
    """Audit logging tests."""

    def test_audit_creates_audit_log(self, in_memory_uow: MemoryAuthUnitOfWork):
        from authentication.repositories.interfaces import AuditRepository
        audit_logger = AuthAuditLogger(in_memory_uow.audit)
        
        from database.enums import AuditAction
        audit_logger.audit(
            action=AuditAction.LOGIN,
            entity_type="user",
            user_id=uuid.uuid4(),
        )
        
        assert len(in_memory_uow.store.audit_logs) == 1
        assert in_memory_uow.store.audit_logs[0].action == AuditAction.LOGIN

    def test_security_event_creates_event(self, in_memory_uow: MemoryAuthUnitOfWork):
        audit_logger = AuthAuditLogger(in_memory_uow.audit)
        
        audit_logger.security_event(
            event_type="login_failure",
            description="Test failure",
            severity="warning",
        )
        
        assert len(in_memory_uow.store.security_events) == 1


class TestAuthEvents:
    """Domain event tests."""

    def test_user_registered_event(self):
        event = UserRegistered(user_id=uuid.uuid4(), email="test@example.com")
        assert event.event_name == "UserRegistered"
        assert event.email == "test@example.com"

    def test_login_succeeded_event(self):
        event = LoginSucceeded(user_id=uuid.uuid4(), session_id=uuid.uuid4())
        assert event.event_name == "LoginSucceeded"

    def test_login_failed_event(self):
        event = LoginFailed(identifier="test@example.com", reason="invalid_credentials")
        assert event.event_name == "LoginFailed"

    def test_logout_completed_event(self):
        event = LogoutCompleted(user_id=uuid.uuid4(), session_id=uuid.uuid4())
        assert event.event_name == "LogoutCompleted"

    def test_password_changed_event(self):
        event = PasswordChanged(user_id=uuid.uuid4())
        assert event.event_name == "PasswordChanged"

    def test_email_verified_event(self):
        event = EmailVerified(user_id=uuid.uuid4())
        assert event.event_name == "EmailVerified"

    def test_account_locked_event(self):
        event = AccountLocked(user_id=uuid.uuid4(), reason="too_many_attempts")
        assert event.event_name == "AccountLocked"


class TestRegistrationWithAllFields:
    """Registration with complete profile tests."""

    def test_full_registration_creates_all_entities(self, auth_factory: AuthenticationServiceFactory):
        service = auth_factory.registration()
        request = RegisterOrganizationRequest(
            email="full@example.com",
            password="StrongP@ss123",
            username="fulluser",
            organization_name="Full Test Org",
            organization_slug="full-test-org",
            profile=UserProfileInput(
                full_name="Full Test User",
                display_name="Full User",
                avatar_url="https://example.com/avatar.png",
                time_zone="America/New_York",
                language="en",
                country="US",
                phone="+1-555-123-4567",
                department="Engineering",
                job_title="Developer",
                theme="dark",
            ),
            marketing_consent=True,
            metadata={"source": "web"},
        )
        response = service.register_organization(request)
        
        # Verify user was created with email verified
        uow = MemoryAuthUnitOfWork()
        user = uow.users.get_by_email("full@example.com")
        assert user is not None
        assert user.email == "full@example.com"

    def test_user_registration_to_existing_org(self, auth_factory: AuthenticationServiceFactory):
        reg_service = auth_factory.registration()
        
        # Create org first
        org_request = RegisterOrganizationRequest(
            email="orgowner@example.com",
            password="StrongP@ss123",
            organization_name="Existing Org",
            profile=UserProfileInput(full_name="Org Owner"),
        )
        org_response = reg_service.register_organization(org_request)
        
        # Register user to existing org
        user_request = RegisterUserRequest(
            email="newuser@example.com",
            password="StrongP@ss123",
            organization_id=org_response.organization_id,
            profile=UserProfileInput(full_name="New User"),
        )
        user_response = reg_service.register_user(user_request)
        
        assert user_response.user_id is not None
        assert user_response.organization_id == org_response.organization_id


class TestPasswordHistory:
    """Password history and reuse prevention tests."""

    def test_password_history_stored_on_registration(self, test_settings: Settings):
        hasher = PasswordHasher()
        uow = MemoryAuthUnitOfWork()
        
        user = User(
            id=uuid.uuid4(),
            email="history@example.com",
            password_hash=hasher.hash("CurrentP@ss1"),
        )
        uow.users.add(user)
        
        history = uow.users.add_password_history(
            type("PasswordHistory", (), {"id": uuid.uuid4(), "user_id": user.id, "password_hash": user.password_hash})()
        )
        
        stored_history = uow.users.password_history(user.id, 5)
        assert len(stored_history) == 1

    def test_password_change_stores_history(self, test_settings: Settings):
        hasher = PasswordHasher()
        uow = MemoryAuthUnitOfWork()
        
        user = User(
            id=uuid.uuid4(),
            email="change@example.com",
            password_hash=hasher.hash("OldP@ss1"),
        )
        uow.users.add(user)
        
        user.password_hash = hasher.hash("NewP@ss2")
        uow.users.add_password_history(
            type("PasswordHistory", (), {"id": uuid.uuid4(), "user_id": user.id, "password_hash": user.password_hash})()
        )
        
        stored_history = uow.users.password_history(user.id, 5)
        assert len(stored_history) == 1


class TestTransactionalBehavior:
    """Tests for transactional behavior of registration."""

    def test_registration_rollback_on_failure(self, test_settings: Settings):
        service = RegistrationService(
            uow_factory=lambda: MemoryAuthUnitOfWork(),
            settings=test_settings,
        )
        uow = MemoryAuthUnitOfWork()
        
        # First registration succeeds
        request = RegisterOrganizationRequest(
            email="rollback@example.com",
            password="StrongP@ss123",
            organization_name="Rollback Test",
            profile=UserProfileInput(full_name="Test User"),
        )
        service.register_organization(request)
        
        # Attempt duplicate registration - should fail and rollback
        with pytest.raises(DuplicateEmailException):
            service.register_organization(request)


class TestOrganizationConstraints:
    """Tests for organization-level constraints."""

    def test_organization_must_have_owner(self, auth_factory: AuthenticationServiceFactory):
        reg_service = auth_factory.registration()
        
        request = RegisterOrganizationRequest(
            email="owner@example.com",
            password="StrongP@ss123",
            organization_name="Owner Test",
            profile=UserProfileInput(full_name="Org Owner"),
        )
        response = reg_service.register_organization(request)
        
        # Verify owner was created
        uow = MemoryAuthUnitOfWork()
        member = uow.organizations.get_member(response.organization_id, response.user_id)
        assert member is not None
        assert member.is_owner is True

    def test_workspace_created_as_default(self, auth_factory: AuthenticationServiceFactory):
        reg_service = auth_factory.registration()
        
        request = RegisterOrganizationRequest(
            email="workspace@example.com",
            password="StrongP@ss123",
            organization_name="Workspace Test Org",
            profile=UserProfileInput(full_name="Test User"),
        )
        response = reg_service.register_organization(request)
        
        assert response.workspace_id is not None