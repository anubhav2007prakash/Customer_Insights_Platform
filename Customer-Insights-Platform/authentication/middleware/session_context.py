"""Framework-agnostic session middleware helpers."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from authentication.services.sessions import SessionService


@dataclass(frozen=True)
class AuthenticatedContext:
    """Identity context produced by validated sessions."""

    user_id: uuid.UUID
    organization_id: uuid.UUID | None
    session_id: uuid.UUID
    permissions: frozenset[str] = frozenset()


class SessionMiddleware:
    """Validates bearer/session tokens and returns an identity context."""

    def __init__(self, session_service: SessionService | None = None) -> None:
        self.session_service = session_service or SessionService()

    def authenticate_token(self, raw_token: str) -> AuthenticatedContext:
        session = self.session_service.validate(raw_token)
        return AuthenticatedContext(
            user_id=session.user_id,
            organization_id=session.organization_id,
            session_id=session.id,
        )
