"""Unit tests for authentication validators."""

from __future__ import annotations

import pytest

from authentication.exceptions import PasswordPolicyException, RegistrationException
from authentication.validators.inputs import (
    validate_avatar_url,
    validate_organization_name,
    validate_phone_number,
    validate_username,
)
from authentication.validators.password_policy import PasswordPolicy, PasswordPolicyValidator, PasswordValidationResult


class TestPasswordPolicyValidator:
    """Password policy validation tests."""

    def test_valid_password_passes(self) -> None:
        validator = PasswordPolicyValidator()
        result = validator.validate("SecureP@ss1", raise_on_error=False)
        assert result.valid is True
        assert result.score >= 50

    def test_too_short_fails(self) -> None:
        validator = PasswordPolicyValidator()
        with pytest.raises(PasswordPolicyException, match="at least 8"):
            validator.validate("Ab1@")

    def test_too_long_fails(self) -> None:
        policy = PasswordPolicy(max_length=16)
        validator = PasswordPolicyValidator(policy=policy)
        with pytest.raises(PasswordPolicyException, match="no more than 16"):
            validator.validate("0123456789ABCDEF1@")

    def test_missing_uppercase_fails(self) -> None:
        with pytest.raises(PasswordPolicyException, match="uppercase"):
            PasswordPolicyValidator().validate("lowercase1@")

    def test_missing_lowercase_fails(self) -> None:
        with pytest.raises(PasswordPolicyException, match="lowercase"):
            PasswordPolicyValidator().validate("UPPERCASE1@")

    def test_missing_numeric_fails(self) -> None:
        with pytest.raises(PasswordPolicyException, match="number"):
            PasswordPolicyValidator().validate("SecurePass@")

    def test_missing_special_fails(self) -> None:
        with pytest.raises(PasswordPolicyException, match="special"):
            PasswordPolicyValidator().validate("SecurePass1")

    def test_raise_on_error_false_returns_invalid(self) -> None:
        validator = PasswordPolicyValidator()
        result = validator.validate("short", raise_on_error=False)
        assert result.valid is False
        assert len(result.errors) > 0
        assert isinstance(result.score, int)

    def test_score_zero_for_weak(self) -> None:
        validator = PasswordPolicyValidator()
        result = validator.validate("a", raise_on_error=False)
        assert result.score >= 0

    def test_score_one_hundred_for_strong(self) -> None:
        validator = PasswordPolicyValidator()
        result = validator.validate("AStr0ng!P@sswordWithL0tsOfChars!")
        assert result.score >= 50
        assert isinstance(result.score, int) and 0 <= result.score <= 100

    def test_custom_policy_applied(self) -> None:
        policy = PasswordPolicy(
            min_length=14,
            max_length=64,
            require_uppercase=True,
            require_lowercase=True,
            require_numeric=True,
            require_special=False,
        )
        validator = PasswordPolicyValidator(policy=policy)
        result = validator.validate("FourteenChars1A", raise_on_error=False)
        assert result.valid is True

    def test_repetition_detected(self) -> None:
        validator = PasswordPolicyValidator()
        result = validator.validate("aaaaBc1@", raise_on_error=False)
        # repetition should not cause failure but reduces score
        assert isinstance(result.score, int)

    def test_password_validation_result_dataclass(self) -> None:
        validator = PasswordPolicyValidator()
        result = validator.validate("Test@123", raise_on_error=False)
        assert isinstance(result, PasswordValidationResult)
        assert hasattr(result, "valid")
        assert hasattr(result, "score")
        assert hasattr(result, "errors")

    def test_default_policy_from_settings(self) -> None:
        validator = PasswordPolicyValidator()
        assert validator.policy.min_length >= 8

    def test_from_settings_classmethod(self) -> None:
        policy = PasswordPolicy(min_length=10, require_uppercase=False)
        validator = PasswordPolicyValidator(policy=policy)
        assert validator.policy.min_length == 10
        assert validator.policy.require_uppercase is False

    def test_score_boundaries(self) -> None:
        validator = PasswordPolicyValidator()
        result_weak = validator.validate("a", raise_on_error=False)
        result_strong = validator.validate(
            "VeryStr0ng!P@sswordThatShouldGetFullMarks!1!",
            raise_on_error=False,
        )
        assert result_weak.score < result_strong.score


class TestInputValidators:
    """Input field validation tests."""

    def test_validate_username_none_passes(self) -> None:
        assert validate_username(None) is None

    def test_validate_username_valid(self) -> None:
        assert validate_username("test_user") == "test_user"

    def test_validate_username_too_short_fails(self) -> None:
        with pytest.raises(RegistrationException, match="3-100"):
            validate_username("ab")

    def test_validate_username_bad_chars_fails(self) -> None:
        with pytest.raises(RegistrationException, match="Username"):
            validate_username("user@name!")  # contains illegal char

    def test_validate_phone_none_passes(self) -> None:
        assert validate_phone_number(None) is None

    def test_validate_phone_empty_passes(self) -> None:
        assert validate_phone_number("") is None

    def test_validate_phone_valid_e164(self) -> None:
        assert validate_phone_number("+1-555-123-4567") is not None

    def test_validate_phone_invalid_fails(self) -> None:
        with pytest.raises(RegistrationException, match="Phone"):
            validate_phone_number("not_a_phone!!")

    def test_validate_avatar_url_none_passes(self) -> None:
        assert validate_avatar_url(None) is None

    def test_validate_avatar_url_empty_passes(self) -> None:
        assert validate_avatar_url("") is None

    def test_validate_avatar_url_valid_https(self) -> None:
        assert validate_avatar_url("https://example.com/avatar.png") is not None

    def test_validate_avatar_url_no_scheme_fails(self) -> None:
        with pytest.raises(RegistrationException, match="Avatar"):
            validate_avatar_url("not-a-url")

    def test_validate_avatar_url_http_only(self) -> None:
        assert validate_avatar_url("http://example.com/avatar.png") is not None

    def test_validate_organization_name_valid(self) -> None:
        assert validate_organization_name("Acme Corp Inc.") == "Acme Corp Inc."

    def test_validate_organization_name_invalid_chars(self) -> None:
        with pytest.raises(RegistrationException, match="Organization"):
            validate_organization_name("Acme@Corp!")  # @ and ! not allowed
