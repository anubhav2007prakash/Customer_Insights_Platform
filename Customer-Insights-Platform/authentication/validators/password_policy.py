"""Configurable password policy validation."""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.config.settings import SecuritySettings, get_settings
from authentication.exceptions import PasswordPolicyException

SPECIAL_RE = re.compile(r"[^A-Za-z0-9]")


@dataclass(frozen=True)
class PasswordPolicy:
    """Runtime password policy."""

    min_length: int = 8
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numeric: bool = True
    require_special: bool = True
    history_count: int = 5
    expiration_days: int = 90

    @classmethod
    def from_settings(cls, settings: SecuritySettings | None = None) -> "PasswordPolicy":
        cfg = settings or get_settings().security
        return cls(
            min_length=cfg.password_min_length,
            max_length=cfg.password_max_length,
            require_uppercase=cfg.password_require_uppercase,
            require_lowercase=cfg.password_require_lowercase,
            require_numeric=cfg.password_require_numeric,
            require_special=cfg.password_require_special,
            history_count=cfg.password_history_count,
            expiration_days=cfg.password_expiration_days,
        )


@dataclass(frozen=True)
class PasswordValidationResult:
    """Password validation details."""

    valid: bool
    score: int
    errors: tuple[str, ...]


class PasswordPolicyValidator:
    """Reusable password policy validator and strength scorer."""

    def __init__(self, policy: PasswordPolicy | None = None) -> None:
        self.policy = policy or PasswordPolicy.from_settings()

    def validate(self, password: str, *, raise_on_error: bool = True) -> PasswordValidationResult:
        errors: list[str] = []
        if len(password) < self.policy.min_length:
            errors.append(f"Password must be at least {self.policy.min_length} characters.")
        if len(password) > self.policy.max_length:
            errors.append(f"Password must be no more than {self.policy.max_length} characters.")
        if self.policy.require_uppercase and not any(ch.isupper() for ch in password):
            errors.append("Password must contain an uppercase letter.")
        if self.policy.require_lowercase and not any(ch.islower() for ch in password):
            errors.append("Password must contain a lowercase letter.")
        if self.policy.require_numeric and not any(ch.isdigit() for ch in password):
            errors.append("Password must contain a number.")
        if self.policy.require_special and not SPECIAL_RE.search(password):
            errors.append("Password must contain a special character.")
        if _has_obvious_repetition(password):
            errors.append("Password contains too much repetition.")

        score = self.score(password)
        result = PasswordValidationResult(valid=not errors, score=score, errors=tuple(errors))
        if errors and raise_on_error:
            raise PasswordPolicyException(
                message=errors[0],
                details={"errors": errors, "score": score},
            )
        return result

    def score(self, password: str) -> int:
        """Return a coarse 0-100 strength score."""
        score = min(len(password) * 4, 40)
        score += 15 if any(ch.isupper() for ch in password) else 0
        score += 15 if any(ch.islower() for ch in password) else 0
        score += 15 if any(ch.isdigit() for ch in password) else 0
        score += 15 if SPECIAL_RE.search(password) else 0
        if _has_obvious_repetition(password):
            score -= 20
        return max(0, min(score, 100))


def _has_obvious_repetition(password: str) -> bool:
    lowered = password.lower()
    return any(ch * 4 in lowered for ch in set(lowered))
