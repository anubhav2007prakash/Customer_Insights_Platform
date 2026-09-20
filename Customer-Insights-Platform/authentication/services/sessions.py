"""Session validation service."""

from __future__ import annotations

from collections.abc import Callable

from core.config.settings import Settings, get_settings
from core.exceptions.base import SessionExpiredError
from authentication.helpers import TokenService, utc_now
from authentication.repositories.interfaces import AuthUnitOfWork
from authentication.repositories.sqlalchemy import SQLAlchemyAuthUnitOfWork
from datetime import timedelta


class SessionService:
    """Validates and revokes sessions."""

    def __init__(
        self,
        uow_factory: Callable[[], AuthUnitOfWork] | None = None,
        *,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.uow_factory = uow_factory or SQLAlchemyAuthUnitOfWork
        self.token_service = TokenService(self.settings.security.secret_key)

    def validate(self, raw_token: str):
        """Return an active session or raise SessionExpiredError."""
        now = utc_now()
        with self.uow_factory() as uow:
            session = uow.sessions.get_active_by_token_hash(self.token_service.hash(raw_token), now)
            if session is None:
                raise SessionExpiredError()
            session.last_seen_at = now
            return session

    def revoke_all_for_user(self, user_id) -> int:
        """Revoke all active sessions for a user."""
        with self.uow_factory() as uow:
            return uow.sessions.revoke_all_for_user(user_id, utc_now())

    def create_session(
        self,
        user_id,
        *,
        organization_id=None,
        device_name=None,
        device_fingerprint=None,
        remember_me: bool = False,
        ip_address: str | None = None,
        user_agent: str | None = None,
        ttl_days: int | None = None,
    ):
        """Create a new session and return (raw_token, session_model).

        The raw token must be delivered to the client; only the hash is stored.
        """
        now = utc_now()
        raw_token = self.token_service.generate()
        token_hash = self.token_service.hash(raw_token)

        # Determine TTL
        if ttl_days is None:
            ttl_days = getattr(self.settings.security, "session_ttl_days", 7)
            if remember_me:
                ttl_days = getattr(self.settings.security, "remember_me_ttl_days", ttl_days)

        expires_at = now + timedelta(days=ttl_days)

        from database.models.auth import UserSession

        session = UserSession(
            user_id=user_id,
            organization_id=organization_id,
            token_hash=token_hash,
            device_fingerprint=device_fingerprint,
            device_name=device_name,
            remember_me=remember_me,
            ip_address=ip_address,
            user_agent=user_agent,
            last_seen_at=now,
            expires_at=expires_at,
        )

        with self.uow_factory() as uow:
            uow.sessions.add(session)

        return raw_token, session

    def list_active_sessions(self, user_id):
        """Return active sessions for a user."""
        now = utc_now()
        with self.uow_factory() as uow:
            try:
                from database.models.auth import UserSession as _US
                from sqlalchemy import select

                rows = uow.session.scalars(select(_US).where(_US.user_id == user_id)).all()
                active = [s for s in rows if s.revoked_at is None and s.expires_at > now]
                return active
            except Exception:
                return []

    def revoke_by_token(self, raw_token: str) -> bool:
        """Revoke a session identified by raw token. Returns True if revoked."""
        now = utc_now()
        token_hash = self.token_service.hash(raw_token)
        with self.uow_factory() as uow:
            session = uow.sessions.get_active_by_token_hash(token_hash, now)
            if not session:
                return False
            uow.sessions.revoke(session, now)
            return True

    def revoke_by_id(self, session_id) -> bool:
        """Revoke a session by its ID."""
        now = utc_now()
        with self.uow_factory() as uow:
            try:
                from database.models.auth import UserSession as _US
                from sqlalchemy import select

                s = uow.session.scalars(select(_US).where(_US.id == session_id)).first()
                if not s:
                    return False
                uow.sessions.revoke(s, now)
                return True
            except Exception:
                return False
