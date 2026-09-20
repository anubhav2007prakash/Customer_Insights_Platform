"""Unit tests for profile building utilities."""

from __future__ import annotations

import uuid

from authentication.schemas import UserProfileInput
from authentication.services.profile import build_profile, profile_completion, split_full_name


class TestSplitFullName:
    """Full name parsing tests."""

    def test_single_name(self) -> None:
        parts = split_full_name("Madonna")
        assert parts.first_name == "Madonna"
        assert parts.last_name is None

    def test_two_names(self) -> None:
        parts = split_full_name("John Smith")
        assert parts.first_name == "John"
        assert parts.last_name == "Smith"

    def test_multi_word_last_name(self) -> None:
        parts = split_full_name("Jane Marie Van Der Waal")
        assert parts.first_name == "Jane"
        assert parts.last_name == "Marie Van Der Waal"

    def test_empty_string(self) -> None:
        parts = split_full_name("")
        assert parts.first_name == ""
        assert parts.last_name is None


class TestProfileCompletion:
    """Profile completion percentage tests."""

    def test_full_profile(self) -> None:
        inp = UserProfileInput(
            full_name="John Smith",
            display_name="Johnny",
            avatar_url="https://example.com/avatar.png",
            time_zone="America/New_York",
            language="en",
            country="US",
            phone="+1-555-123-4567",
            department="Engineering",
            job_title="Engineer",
        )
        assert profile_completion(inp) == 100

    def test_empty_profile(self) -> None:
        inp = UserProfileInput(full_name="John Smith")
        # Only full_name is set, everything else defaults to None or their default
        # time_zone defaults to "UTC" and language defaults to "en" - those count
        assert profile_completion(inp) < 100

    def test_partial_profile(self) -> None:
        inp = UserProfileInput(
            full_name="Jane Doe",
            display_name="Jane",
            time_zone="UTC",
            language="en",
        )
        assert 20 <= profile_completion(inp) <= 60


class TestBuildProfile:
    """Profile ORM model building tests."""

    def test_build_profile_creates_model(self) -> None:
        user_id = uuid.uuid4()
        inp = UserProfileInput(
            full_name="Alice Johnson",
            display_name="Alice",
            time_zone="Europe/London",
            language="en",
            country="GB",
        )
        profile = build_profile(user_id, inp)
        assert profile.user_id == user_id
        assert profile.first_name == "Alice"
        assert profile.last_name == "Johnson"
        assert profile.display_name == "Alice"
        assert profile.timezone == "Europe/London"
        assert profile.language == "en"
        assert profile.country == "GB"
        assert profile.locale == "en-GB"
        assert profile.profile_completion > 0

    def test_build_profile_no_last_name(self) -> None:
        user_id = uuid.uuid4()
        inp = UserProfileInput(
            full_name="Prince",
            display_name="The Artist",
            time_zone="UTC",
            language="en",
        )
        profile = build_profile(user_id, inp)
        assert profile.first_name == "Prince"
        assert profile.last_name is None
        assert profile.display_name == "The Artist"

    def test_build_profile_country_none_locale(self) -> None:
        user_id = uuid.uuid4()
        inp = UserProfileInput(
            full_name="Test User",
            time_zone="UTC",
            language="fr",
            country=None,
        )
        profile = build_profile(user_id, inp)
        assert profile.country is None
        assert profile.locale == "fr"
