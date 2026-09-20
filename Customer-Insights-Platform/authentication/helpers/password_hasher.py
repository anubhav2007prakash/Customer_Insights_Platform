"""Password hashing and verification using bcrypt."""

from __future__ import annotations

from core.config.settings import get_settings


class PasswordHasher:
    """Bcrypt password hasher with algorithm upgrade support."""

    def __init__(self, rounds: int | None = None) -> None:
        self._rounds = rounds or get_settings().security.bcrypt_rounds

    def hash(self, password: str) -> str:
        """Hash a plaintext password with automatic salt generation."""
        import bcrypt

        salt = bcrypt.gensalt(rounds=self._rounds)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify(self, password: str, password_hash: str | None) -> bool:
        """Verify a password in constant-time."""
        if not password_hash:
            return False
        try:
            import bcrypt

            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except (TypeError, ValueError):
            return False

    def needs_update(self, password_hash: str) -> bool:
        """Return whether the hash should be upgraded on next successful login."""
        return not password_hash.startswith("$2b$")
