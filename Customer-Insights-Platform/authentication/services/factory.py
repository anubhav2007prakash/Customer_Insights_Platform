"""Factory for composing authentication services."""

from __future__ import annotations

from collections.abc import Callable

from core.config.settings import Settings, get_settings
from core.interfaces.event_bus import EventBusPort
from authentication.repositories.interfaces import AuthUnitOfWork
from authentication.repositories.memory import MemoryAuthUnitOfWork
from authentication.repositories.sqlalchemy import SQLAlchemyAuthUnitOfWork
from authentication.services.email_verification import EmailVerificationService
from authentication.services.login import AuthenticationService
from authentication.services.password_reset import PasswordResetService
from authentication.services.providers import EmailProvider, MockEmailProvider
from authentication.services.registration import RegistrationService
from authentication.services.sessions import SessionService


class AuthenticationServiceFactory:
    """Composes auth services with shared dependencies."""

    def __init__(
        self,
        *,
        uow_factory: Callable[[], AuthUnitOfWork] | None = None,
        settings: Settings | None = None,
        email_provider: EmailProvider | None = None,
        event_bus: EventBusPort | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.uow_factory = uow_factory or MemoryAuthUnitOfWork
        self.email_provider = email_provider or MockEmailProvider()
        self.event_bus = event_bus

    def registration(self) -> RegistrationService:
        return RegistrationService(
            self.uow_factory,
            settings=self.settings,
            email_provider=self.email_provider,
            event_bus=self.event_bus,
        )

    def authentication(self) -> AuthenticationService:
        return AuthenticationService(self.uow_factory, settings=self.settings, event_bus=self.event_bus)

    def password_reset(self) -> PasswordResetService:
        return PasswordResetService(
            self.uow_factory,
            settings=self.settings,
            email_provider=self.email_provider,
            event_bus=self.event_bus,
        )

    def email_verification(self) -> EmailVerificationService:
        return EmailVerificationService(
            self.uow_factory,
            settings=self.settings,
            email_provider=self.email_provider,
            event_bus=self.event_bus,
        )

    def sessions(self) -> SessionService:
        return SessionService(self.uow_factory, settings=self.settings)
