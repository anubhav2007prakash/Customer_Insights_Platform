"""Unit tests for registration service."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from core.config.settings import Settings
from core.events.bus import InMemoryEventBus
from database.enums import AuditAction, OrganizationStatus, UserStatus
from authentication.events import UserRegistered
from authentication.exceptions import (
    DuplicateEmailException,
    DuplicateOrganizationException,
    DuplicateUsernameException,
    PasswordPolicyException,
)
from authentication.helpers import PasswordHasher, utc_now
from authentication.repositories.memory import MemoryAuthUnitOfWork
from authentication.schemas import RegisterOrganizationRequest, RegisterUserRequest, UserProfileInput
from authentication.services.providers import MockEmailProvider
from authentication.services.registration import RegistrationService


@pytest.fixture()
def reg_service(uow: MemoryAuthUnitOfWork, settings: Settings, event_bus: InMemoryEventBus) -> RegistrationService:
    return RegistrationService(
        uow_factory=lambda: uow,
        settings=settings,
        email_provider=MockEmailProvider(),
        event_bus=event_bus,
        password_hasher=PasswordHasher(rounds=4),
    )


def make_profile(full_name: str = "Test User") -> UserProfileInput:
    return UserProfileInput(full_name=full_name)


class TestRegisterOrganization:
    """Organization + owner registration workflow."""

    def test_register_organization_creates_all_entities(self, reg_service: RegistrationService) -> None:
        request = RegisterOrganizationRequest(
            email="admin@acme.com",
            password="SecureP@ss1",
            organization_name="Acme Corp",
            profile=make_profile("Admin User"),
        )
        response = reg_service.register_organization(request)
        assert response.user_id is not None
        assert response.organization_id is not None
        assert response.workspace_id is not None
        assert response.email == "admin@acme.com"
        assert response.status == UserStatus.PENDING_VERIFICATION.value
        assert response.verification_required is True

    def test_register_organization_creates_owner_role(self, reg_service: RegistrationService, uow: MemoryAuthUnitOfWork) -> None:
        request = RegisterOrganizationRequest(
            email="owner@acme.com",
            password="SecureP@ss1",
            organization_name="Acme Corp",
            profile=make_profile("Owner"),
        )
        response = reg_service.register_organization(request)
        with uow:
            org_id = response.organization_id
            # Check role exists
            roles = [r for r in uow.roles.store.roles if r.organization_id == org_id]
            assert any(r.name == "Owner" for r in roles)
            # Check member is owner
            members = [m for m in uow.organizations.store.members if m.organization_id == org_id]
            assert any(m.is_owner for m in members)

    def test_register_organization_creates_profile_and_preferences(
        self,
        reg_service: RegistrationService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        request = RegisterOrganizationRequest(
            email="user@acme.com",
            password="SecureP@ss1",
            organization_name="Acme Corp",
            profile=make_profile("Jane Doe"),
        )
        response = reg_service.register_organization(request)
        with uow:
            user = uow.users.get_by_id(response.user_id)
            assert user is not None
            profile = user.profile
            assert profile is not None
            assert profile.display_name == "Jane Doe"
            assert profile.first_name == "Jane"
            assert profile.last_name == "Doe"
            prefs = [p for p in uow.users.store.preferences if p.user_id == response.user_id]
            assert len(prefs) == 1
            assert prefs[0].theme == "light"

    def test_register_organization_creates_audit_log(self, reg_service: RegistrationService, uow: MemoryAuthUnitOfWork) -> None:
        request = RegisterOrganizationRequest(
            email="audit@acme.com",
            password="SecureP@ss1",
            organization_name="Audit Corp",
            profile=make_profile("Audit User"),
        )
        response = reg_service.register_organization(request)
        with uow:
            logs = [l for l in uow.audit.store.audit_logs if l.entity_id == response.user_id]
            assert len(logs) >= 1
            assert logs[0].action == AuditAction.CREATE

    def test_register_organization_sends_verification_email(
        self,
        reg_service: RegistrationService,
        settings: Settings,
    ) -> None:
        provider = MockEmailProvider()
        service = RegistrationService(
            uow_factory=lambda: reg_service.uow_factory(),
            settings=settings,
            email_provider=provider,
            password_hasher=PasswordHasher(rounds=4),
        )
        request = RegisterOrganizationRequest(
            email="emailtest@acme.com",
            password="SecureP@ss1",
            organization_name="Email Corp",
            profile=make_profile("Email User"),
        )
        service.register_organization(request)
        assert len(provider.sent) == 1
        assert provider.sent[0].kind == "verification"
        assert provider.sent[0].email == "emailtest@acme.com"

    def test_register_organization_publishes_event(
        self,
        reg_service: RegistrationService,
        event_bus: InMemoryEventBus,
    ) -> None:
        received_events: list[UserRegistered] = []
        event_bus.subscribe(UserRegistered, lambda e: received_events.append(e))
        request = RegisterOrganizationRequest(
            email="event@acme.com",
            password="SecureP@ss1",
            organization_name="Event Corp",
            profile=make_profile("Event User"),
        )
        response = reg_service.register_organization(request)
        assert len(received_events) == 1
        assert received_events[0].user_id == response.user_id
        assert received_events[0].email == "event@acme.com"

    def test_duplicate_email_raises_error(self, reg_service: RegistrationService) -> None:
        request = RegisterOrganizationRequest(
            email="dup@acme.com",
            password="SecureP@ss1",
            organization_name="First Corp",
            profile=make_profile("User"),
        )
        reg_service.register_organization(request)
        with pytest.raises(DuplicateEmailException):
            reg_service.register_organization(request)

    def test_duplicate_organization_slug_raises_error(self, reg_service: RegistrationService) -> None:
        request = RegisterOrganizationRequest(
            email="a@acme.com",
            password="SecureP@ss1",
            organization_name="Same Corp",
            profile=make_profile("User A"),
        )
        reg_service.register_organization(request)
        with pytest.raises(DuplicateOrganizationException):
            reg_service.register_organization(
                RegisterOrganizationRequest(
                    email="b@acme.com",
                    password="SecureP@ss1",
                    organization_name="Same Corp",  # same slug
                    profile=make_profile("User B"),
                )
            )

    def test_weak_password_raises_error(self, reg_service: RegistrationService) -> None:
        with pytest.raises(PasswordPolicyException):
            reg_service.register_organization(
                RegisterOrganizationRequest(
                    email="weak@acme.com",
                    password="short",
                    organization_name="Weak Corp",
                    profile=make_profile("Weak User"),
                )
            )

    def test_duplicate_username_raises_error(self, reg_service: RegistrationService) -> None:
        request = RegisterOrganizationRequest(
            email="u1@acme.com",
            password="SecureP@ss1",
            username="sameuser",
            organization_name="Org One",
            profile=make_profile("User One"),
        )
        reg_service.register_organization(request)
        with pytest.raises(DuplicateUsernameException):
            reg_service.register_organization(
                RegisterOrganizationRequest(
                    email="u2@acme.com",
                    password="SecureP@ss1",
                    username="sameuser",
                    organization_name="Org Two",
                    profile=make_profile("User Two"),
                )
            )

    def test_username_uniqueness_configurable(self, reg_service: RegistrationService, settings: Settings) -> None:
        settings.security.username_unique = False
        reg_service.register_organization(
            RegisterOrganizationRequest(
                email="a1@acme.com",
                password="SecureP@ss1",
                username="shared",
                organization_name="Org A",
                profile=make_profile("User A"),
            )
        )
        # Should not raise with username_unique=False
        reg_service.register_organization(
            RegisterOrganizationRequest(
                email="a2@acme.com",
                password="SecureP@ss1",
                username="shared",
                organization_name="Org B",
                profile=make_profile("User B"),
            )
        )

    def test_custom_organization_slug(self, reg_service: RegistrationService, uow: MemoryAuthUnitOfWork) -> None:
        request = RegisterOrganizationRequest(
            email="slug@acme.com",
            password="SecureP@ss1",
            organization_name="Slug Corp",
            organization_slug="custom-slug",
            profile=make_profile("Slug User"),
        )
        response = reg_service.register_organization(request)
        with uow:
            org = uow.organizations.get_by_id(response.organization_id)
            assert org is not None
            assert org.slug == "custom-slug"

    def test_require_verified_email_sets_pending(self, reg_service: RegistrationService, settings: Settings) -> None:
        settings.security.require_verified_email = True
        request = RegisterOrganizationRequest(
            email="pending@acme.com",
            password="SecureP@ss1",
            organization_name="Pending Corp",
            profile=make_profile("Pending User"),
        )
        response = reg_service.register_organization(request)
        assert response.status == UserStatus.PENDING_VERIFICATION.value

    def test_not_require_verified_email_sets_active(self, reg_service: RegistrationService, settings: Settings) -> None:
        settings.security.require_verified_email = False
        request = RegisterOrganizationRequest(
            email="active@acme.com",
            password="SecureP@ss1",
            organization_name="Active Corp",
            profile=make_profile("Active User"),
        )
        response = reg_service.register_organization(request)
        assert response.status == UserStatus.ACTIVE.value


class TestRegisterUser:
    """User registration into existing organization."""

    def test_register_user_into_existing_org(
        self,
        reg_service: RegistrationService,
        uow: MemoryAuthUnitOfWork,
    ) -> None:
        # First seed an org
        org_request = RegisterOrganizationRequest(
            email="org@acme.com",
            password="SecureP@ss1",
            organization_name="Main Corp",
            profile=make_profile("Org Owner"),
        )
        org_response = reg_service.register_organization(org_request)

        user_request = RegisterUserRequest(
            email="member@acme.com",
            password="SecureP@ss1",
            organization_id=org_response.organization_id,
            profile=make_profile("Team Member"),
        )
        user_response = reg_service.register_user(user_request)
        assert user_response.user_id is not None
        assert user_response.organization_id == org_response.organization_id
        assert user_response.email == "member@acme.com"

        with uow:
            member = uow.organizations.get_member(org_response.organization_id, user_response.user_id)
            assert member is not None
            assert member.is_owner is False

    def test_register_user_nonexistent_org_raises_error(self, reg_service: RegistrationService) -> None:
        import uuid

        with pytest.raises(Exception):
            reg_service.register_user(
                RegisterUserRequest(
                    email="fail@acme.com",
                    password="SecureP@ss1",
                    organization_id=uuid.uuid4(),
                    profile=make_profile("Fail User"),
                )
            )

    def test_register_user_duplicate_email_raises_error(self, reg_service: RegistrationService) -> None:
        org_request = RegisterOrganizationRequest(
            email="org2@acme.com",
            password="SecureP@ss1",
            organization_name="Org Two",
            profile=make_profile("Owner"),
        )
        org_response = reg_service.register_organization(org_request)

        reg_service.register_user(
            RegisterUserRequest(
                email="dup2@acme.com",
                password="SecureP@ss1",
                organization_id=org_response.organization_id,
                profile=make_profile("First"),
            )
        )
        with pytest.raises(DuplicateEmailException):
            reg_service.register_user(
                RegisterUserRequest(
                    email="dup2@acme.com",
                    password="SecureP@ss1",
                    organization_id=org_response.organization_id,
                    profile=make_profile("Second"),
                )
            )
