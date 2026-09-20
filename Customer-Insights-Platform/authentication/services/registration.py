"""Transactional registration workflows."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import timedelta

from core.config.settings import Settings, get_settings
from core.events.base import EventMetadata
from core.interfaces.event_bus import EventBusPort
from database.enums import AuditAction, NotificationChannel, NotificationPriority, OrganizationStatus, UserStatus
from database.models.auth import EmailVerificationToken, NotificationSetting, PasswordHistory, User, UserPreference
from database.models.notifications import Notification
from database.models.tenant import Organization, OrganizationMember, Role, UserRole, Workspace
from authentication.audit import AuthAuditLogger
from authentication.constants.defaults import (
    DEFAULT_NOTIFICATION_EVENTS,
    DEFAULT_WORKSPACE_NAME,
    DEFAULT_WORKSPACE_SLUG,
    MEMBER_ROLE,
    OWNER_ROLE,
)
from authentication.events import UserRegistered
from authentication.exceptions import (
    DuplicateEmailException,
    DuplicateOrganizationException,
    DuplicateUsernameException,
    RegistrationException,
)
from authentication.helpers import PasswordHasher, TokenService, normalize_email, normalize_username, slugify, utc_now
from authentication.repositories.interfaces import AuthUnitOfWork
from authentication.repositories.sqlalchemy import SQLAlchemyAuthUnitOfWork
from authentication.schemas import RegisterOrganizationRequest, RegisterUserRequest, RegistrationResponse
from authentication.services.profile import build_profile
from authentication.services.providers import EmailProvider, MockEmailProvider
from authentication.validators import PasswordPolicyValidator


class RegistrationService:
    """Registration application service."""

    def __init__(
        self,
        uow_factory: Callable[[], AuthUnitOfWork] | None = None,
        *,
        settings: Settings | None = None,
        email_provider: EmailProvider | None = None,
        event_bus: EventBusPort | None = None,
        password_hasher: PasswordHasher | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.uow_factory = uow_factory or SQLAlchemyAuthUnitOfWork
        self.email_provider = email_provider or MockEmailProvider()
        self.event_bus = event_bus
        self.password_hasher = password_hasher or PasswordHasher()
        self.password_validator = PasswordPolicyValidator()
        self.token_service = TokenService(self.settings.security.secret_key)

    def register_organization(self, request: RegisterOrganizationRequest) -> RegistrationResponse:
        """Register a new organization, default workspace, and owner."""
        self.password_validator.validate(request.password)
        email = normalize_email(str(request.email))
        username = normalize_username(request.username)
        organization_slug = request.organization_slug or slugify(request.organization_name)
        now = utc_now()

        with self.uow_factory() as uow:
            if uow.users.get_by_email(email):
                raise DuplicateEmailException(details={"email": email})
            if username and self.settings.security.username_unique and uow.users.get_by_username(username):
                raise DuplicateUsernameException(details={"username": username})
            if uow.organizations.get_by_slug(organization_slug):
                raise DuplicateOrganizationException(details={"slug": organization_slug})

            organization = Organization(
                id=uuid.uuid4(),
                name=request.organization_name,
                slug=organization_slug,
                status=OrganizationStatus.TRIAL,
                metadata_={"registration": request.metadata, "marketing_consent": request.marketing_consent},
            )
            workspace = Workspace(
                id=uuid.uuid4(),
                organization_id=organization.id,
                name=DEFAULT_WORKSPACE_NAME,
                slug=DEFAULT_WORKSPACE_SLUG,
                is_default=True,
            )
            owner_role = Role(
                id=uuid.uuid4(),
                organization_id=organization.id,
                name=OWNER_ROLE,
                description="Organization owner with full administrative access.",
                is_system=True,
            )
            user = self._build_user(email=email, username=username, password=request.password, now=now)

            uow.organizations.add(organization)
            uow.organizations.add_workspace(workspace)
            uow.roles.add(owner_role)
            uow.users.add(user)
            uow.users.add_profile(build_profile(user.id, request.profile))
            self._initialize_user_preferences(uow, user.id, organization.id, request.profile.theme, request.profile.preferences)
            uow.organizations.add_member(
                OrganizationMember(
                    id=uuid.uuid4(),
                    organization_id=organization.id,
                    user_id=user.id,
                    role_id=owner_role.id,
                    is_owner=True,
                    joined_at=now,
                )
            )
            uow.roles.assign(UserRole(id=uuid.uuid4(), organization_id=organization.id, user_id=user.id, role_id=owner_role.id))
            self._record_password_history(uow, user)
            verification_token = self._create_verification_token(uow, user, email)
            self._create_welcome_notification(uow, organization.id, user.id)
            audit = AuthAuditLogger(uow.audit)
            audit.audit(
                action=AuditAction.CREATE,
                entity_type="user",
                organization_id=organization.id,
                user_id=user.id,
                entity_id=user.id,
                new_values={"email": email, "status": user.status.value},
            )
            self.email_provider.send_verification_email(
                email=email,
                token=verification_token,
                full_name=request.profile.full_name,
            )

            if self.event_bus:
                self.event_bus.publish(
                    UserRegistered(
                        metadata=EventMetadata(organization_id=organization.id, user_id=user.id),
                        user_id=user.id,
                        email=email,
                    )
                )

            return RegistrationResponse(
                user_id=user.id,
                organization_id=organization.id,
                workspace_id=workspace.id,
                email=email,
                status=user.status.value,
                verification_required=self.settings.security.require_verified_email,
            )

    def register_user(self, request: RegisterUserRequest) -> RegistrationResponse:
        """Register a user into an existing organization."""
        self.password_validator.validate(request.password)
        email = normalize_email(str(request.email))
        username = normalize_username(request.username)
        now = utc_now()

        with self.uow_factory() as uow:
            if uow.users.get_by_email(email):
                raise DuplicateEmailException(details={"email": email})
            if username and self.settings.security.username_unique and uow.users.get_by_username(username):
                raise DuplicateUsernameException(details={"username": username})

            organization = (
                uow.organizations.get_by_id(request.organization_id)
                if request.organization_id
                else uow.organizations.get_by_slug(request.organization_slug or "")
            )
            if organization is None:
                raise RegistrationException("Organization was not found.")

            role = uow.roles.get_by_name(organization.id, request.role_name)
            if role is None:
                role = uow.roles.add(
                    Role(
                        id=uuid.uuid4(),
                        organization_id=organization.id,
                        name=request.role_name or MEMBER_ROLE,
                        description="Default organization member.",
                        is_system=True,
                    )
                )

            user = self._build_user(email=email, username=username, password=request.password, now=now)
            uow.users.add(user)
            uow.users.add_profile(build_profile(user.id, request.profile))
            self._initialize_user_preferences(uow, user.id, organization.id, request.profile.theme, request.profile.preferences)
            uow.organizations.add_member(
                OrganizationMember(
                    id=uuid.uuid4(),
                    organization_id=organization.id,
                    user_id=user.id,
                    role_id=role.id,
                    is_owner=False,
                    joined_at=now,
                )
            )
            uow.roles.assign(UserRole(id=uuid.uuid4(), organization_id=organization.id, user_id=user.id, role_id=role.id))
            self._record_password_history(uow, user)
            verification_token = self._create_verification_token(uow, user, email)
            AuthAuditLogger(uow.audit).audit(
                action=AuditAction.CREATE,
                entity_type="user",
                organization_id=organization.id,
                user_id=user.id,
                entity_id=user.id,
                new_values={"email": email, "status": user.status.value},
            )
            self.email_provider.send_verification_email(
                email=email,
                token=verification_token,
                full_name=request.profile.full_name,
            )
            return RegistrationResponse(
                user_id=user.id,
                organization_id=organization.id,
                workspace_id=None,
                email=email,
                status=user.status.value,
                verification_required=self.settings.security.require_verified_email,
            )

    def _build_user(self, *, email: str, username: str | None, password: str, now) -> User:
        password_hash = self.password_hasher.hash(password)
        return User(
            id=uuid.uuid4(),
            email=email,
            username=username,
            password_hash=password_hash,
            status=UserStatus.PENDING_VERIFICATION if self.settings.security.require_verified_email else UserStatus.ACTIVE,
            email_verified_at=None if self.settings.security.require_verified_email else now,
            password_changed_at=now,
            password_expires_at=now + timedelta(days=self.settings.security.password_expiration_days),
            failed_login_attempts=0,
        )

    def _record_password_history(self, uow: AuthUnitOfWork, user: User) -> None:
        if not user.password_hash:
            return
        uow.users.add_password_history(
            PasswordHistory(id=uuid.uuid4(), user_id=user.id, password_hash=user.password_hash)
        )

    def _create_verification_token(self, uow: AuthUnitOfWork, user: User, email: str) -> str:
        token = self.token_service.generate()
        uow.tokens.add_email_verification(
            EmailVerificationToken(
                id=uuid.uuid4(),
                user_id=user.id,
                email=email,
                token_hash=token.token_hash,
                expires_at=utc_now() + timedelta(hours=self.settings.security.email_verification_token_ttl_hours),
            )
        )
        return token.raw

    def _initialize_user_preferences(
        self,
        uow: AuthUnitOfWork,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        theme: str,
        preferences: dict,
    ) -> None:
        uow.users.add_preference(
            UserPreference(id=uuid.uuid4(), user_id=user_id, theme=theme, preferences=preferences, dashboard_layout={})
        )
        for event_type in DEFAULT_NOTIFICATION_EVENTS:
            uow.notifications.add_setting(
                NotificationSetting(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    organization_id=organization_id,
                    channel="email",
                    event_type=event_type,
                    is_enabled=True,
                )
            )

    def _create_welcome_notification(self, uow: AuthUnitOfWork, organization_id: uuid.UUID, user_id: uuid.UUID) -> None:
        uow.notifications.add(
            Notification(
                id=uuid.uuid4(),
                organization_id=organization_id,
                user_id=user_id,
                title="Welcome to InsightForge AI",
                body="Your workspace is ready.",
                channel=NotificationChannel.IN_APP,
                priority=NotificationPriority.NORMAL,
                metadata_={"event": "product.welcome"},
            )
        )
