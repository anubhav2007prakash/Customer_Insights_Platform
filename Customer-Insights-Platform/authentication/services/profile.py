"""Profile creation helpers."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from authentication.schemas import UserProfileInput
from database.models.auth import UserProfile


@dataclass(frozen=True)
class NameParts:
    first_name: str
    last_name: str | None


def split_full_name(full_name: str) -> NameParts:
    """Split full name into first/last with conservative assumptions."""
    parts = full_name.strip().split()
    if not parts:
        return NameParts(first_name="", last_name=None)
    if len(parts) == 1:
        return NameParts(first_name=parts[0], last_name=None)
    return NameParts(first_name=parts[0], last_name=" ".join(parts[1:]))


def profile_completion(profile: UserProfileInput) -> int:
    """Calculate profile completion percentage from expected fields."""
    values = [
        profile.full_name,
        profile.display_name,
        profile.avatar_url,
        profile.time_zone,
        profile.language,
        profile.country,
        profile.phone,
        profile.department,
        profile.job_title,
    ]
    completed = sum(1 for value in values if value)
    return int((completed / len(values)) * 100)


def build_profile(user_id: uuid.UUID, profile: UserProfileInput) -> UserProfile:
    """Build the ORM profile model for a user."""
    name = split_full_name(profile.full_name)
    return UserProfile(
        id=uuid.uuid4(),
        user_id=user_id,
        first_name=name.first_name,
        last_name=name.last_name,
        display_name=profile.display_name or profile.full_name,
        avatar_url=profile.avatar_url,
        phone=profile.phone,
        country=profile.country.upper() if profile.country else None,
        department=profile.department,
        job_title=profile.job_title,
        timezone=profile.time_zone,
        language=profile.language,
        locale=f"{profile.language}-{profile.country.upper()}" if profile.country else profile.language,
        notification_settings=profile.notification_settings,
        profile_completion=profile_completion(profile),
    )
