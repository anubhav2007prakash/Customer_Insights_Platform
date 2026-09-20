"""Security-focused input validators."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from authentication.exceptions import RegistrationException

USERNAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{2,99}$")
PHONE_RE = re.compile(r"^\+?[0-9 .()\-]{7,32}$")
ORG_NAME_RE = re.compile(r"^[\w .,&'()\-]{2,255}$", re.UNICODE)


def validate_username(username: str | None) -> str | None:
    """Validate optional username."""
    if username is None:
        return None
    value = username.strip()
    if not USERNAME_RE.fullmatch(value):
        raise RegistrationException(
            "Username must be 3-100 characters and may contain letters, numbers, dots, underscores, or hyphens.",
            details={"field": "username"},
        )
    return value


def validate_phone_number(phone: str | None) -> str | None:
    """Validate optional E.164-ish phone number."""
    if not phone:
        return None
    value = phone.strip()
    if not PHONE_RE.fullmatch(value):
        raise RegistrationException("Phone number is malformed.", details={"field": "phone"})
    return value


def validate_avatar_url(avatar_url: str | None) -> str | None:
    """Validate optional avatar URL."""
    if not avatar_url:
        return None
    parsed = urlparse(avatar_url.strip())
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise RegistrationException("Avatar URL is malformed.", details={"field": "avatar_url"})
    return avatar_url.strip()[:512]


def validate_organization_name(name: str) -> str:
    """Validate tenant organization name."""
    value = name.strip()
    if not ORG_NAME_RE.fullmatch(value):
        raise RegistrationException(
            "Organization name contains unsupported characters.",
            details={"field": "organization_name"},
        )
    return value
