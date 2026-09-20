"""Normalization and slug helpers."""

from __future__ import annotations

import re
import unicodedata


def normalize_email(email: str) -> str:
    """Normalize email for lookup and uniqueness checks."""
    return email.strip().lower()


def normalize_username(username: str | None) -> str | None:
    """Normalize optional usernames."""
    if username is None:
        return None
    value = username.strip().lower()
    return value or None


def slugify(value: str) -> str:
    """Create a stable ASCII slug."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return slug[:100] or "organization"
