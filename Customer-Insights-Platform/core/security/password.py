"""Password hashing using bcrypt."""

from __future__ import annotations

import bcrypt

from core.config.settings import get_settings
from core.exceptions.base import ValidationError


class PasswordHasher:
    """Injectable password hasher service."""

    def hash(self, password: str) -> str:
        """Hash a plaintext password."""
        settings = get_settings()
        if len(password) < settings.security.password_min_length:
            raise ValidationError(
                message=f"Password must be at least {settings.security.password_min_length} characters.",
            )
        rounds = settings.security.bcrypt_rounds
        salt = bcrypt.gensalt(rounds=rounds)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify(self, password: str, password_hash: str) -> bool:
        """Verify password against stored hash."""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except (ValueError, TypeError):
            return False


def verify_password(password: str, password_hash: str) -> bool:
    """Convenience function for password verification."""
    return PasswordHasher().verify(password, password_hash)
