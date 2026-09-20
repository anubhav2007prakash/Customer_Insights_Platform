"""Unit tests for authentication helpers."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from authentication.helpers import PasswordHasher, TokenService, normalize_email, normalize_username, slugify, utc_now
from authentication.helpers.tokens import TokenPair


class TestPasswordHasher:
    """Password hashing and verification tests."""

    def test_hash_returns_bcrypt_string(self, password_hasher: PasswordHasher) -> None:
        hashed = password_hasher.hash("SecureP@ss1")
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self, password_hasher: PasswordHasher) -> None:
        hashed = password_hasher.hash("SecureP@ss1")
        assert password_hasher.verify("SecureP@ss1", hashed) is True

    def test_verify_incorrect_password(self, password_hasher: PasswordHasher) -> None:
        hashed = password_hasher.hash("SecureP@ss1")
        assert password_hasher.verify("WrongP@ss1", hashed) is False

    def test_verify_none_hash_returns_false(self, password_hasher: PasswordHasher) -> None:
        assert password_hasher.verify("SecureP@ss1", None) is False

    def test_verify_empty_hash_returns_false(self, password_hasher: PasswordHasher) -> None:
        assert password_hasher.verify("SecureP@ss1", "") is False

    def test_needs_update_returns_false_for_bcrypt(self, password_hasher: PasswordHasher) -> None:
        hashed = password_hasher.hash("SecureP@ss1")
        assert password_hasher.needs_update(hashed) is False

    def test_needs_update_returns_true_for_plain(self, password_hasher: PasswordHasher) -> None:
        assert password_hasher.needs_update("plaintext") is True

    def test_two_hashes_of_same_password_differ(self, password_hasher: PasswordHasher) -> None:
        h1 = password_hasher.hash("SecureP@ss1")
        h2 = password_hasher.hash("SecureP@ss1")
        assert h1 != h2  # different salts

    def test_verify_empty_password(self, password_hasher: PasswordHasher) -> None:
        hashed = password_hasher.hash("")
        assert password_hasher.verify("", hashed) is True


class TestTokenService:
    """Token generation and hashing tests."""

    def test_generate_returns_token_pair(self, token_service: TokenService) -> None:
        pair = token_service.generate()
        assert isinstance(pair, TokenPair)
        assert isinstance(pair.raw, str)
        assert isinstance(pair.token_hash, str)
        assert len(pair.raw) > 32
        assert len(pair.token_hash) == 64  # SHA-256 hex

    def test_generate_produces_different_tokens(self, token_service: TokenService) -> None:
        t1 = token_service.generate()
        t2 = token_service.generate()
        assert t1.raw != t2.raw
        assert t1.token_hash != t2.token_hash

    def test_hash_is_deterministic(self, token_service: TokenService) -> None:
        raw = "some-test-token-123"
        assert token_service.hash(raw) == token_service.hash(raw)

    def test_verify_correct_token(self, token_service: TokenService) -> None:
        pair = token_service.generate()
        assert token_service.verify(pair.raw, pair.token_hash) is True

    def test_verify_incorrect_token(self, token_service: TokenService) -> None:
        pair = token_service.generate()
        assert token_service.verify("wrong-token", pair.token_hash) is False

    def test_verify_wrong_hash(self, token_service: TokenService) -> None:
        assert token_service.verify("token", "different-hash") is False

    def test_custom_bytes_length(self, token_service: TokenService) -> None:
        pair = token_service.generate(bytes_length=16)
        assert len(pair.raw) >= 21  # base64url of 16 bytes


class TestNormalization:
    """Email, username, and slug normalization tests."""

    def test_normalize_email_lowercases(self) -> None:
        assert normalize_email("Test@Example.COM") == "test@example.com"

    def test_normalize_email_strips(self) -> None:
        assert normalize_email("  user@example.com  ") == "user@example.com"

    def test_normalize_username_returns_none_for_none(self) -> None:
        assert normalize_username(None) is None

    def test_normalize_username_returns_none_for_empty(self) -> None:
        assert normalize_username("  ") is None

    def test_normalize_username_lowercases(self) -> None:
        assert normalize_username("TestUser") == "testuser"

    def test_slugify_basic(self) -> None:
        assert slugify("Hello World") == "hello-world"

    def test_slugify_special_chars(self) -> None:
        assert slugify("My Org!@#$%^") == "my-org"

    def test_slugify_unicode(self) -> None:
        assert slugify("Café München") in ("cafe-munchen", "caf-mnchen")

    def test_slugify_empty_fallback(self) -> None:
        slug = slugify("!!!")
        assert slug == "organization" or slug == ""

    def test_slugify_max_length(self) -> None:
        long = slugify("a" * 200)
        assert len(long) <= 100


class TestTime:
    """UTC time helpers."""

    def test_utc_now_returns_aware_datetime(self) -> None:
        now = utc_now()
        assert isinstance(now, datetime)
        assert now.tzinfo is not None
        assert now.tzinfo == timezone.utc
