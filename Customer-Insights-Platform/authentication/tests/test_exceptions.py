"""Unit tests for authentication exception hierarchy."""

from __future__ import annotations

from authentication.exceptions import (
    AccountLockedException,
    AccountStatusException,
    AuthenticationException,
    BusinessRuleException,
    DuplicateEmailException,
    DuplicateOrganizationException,
    DuplicateUsernameException,
    EmailNotVerifiedException,
    InvalidCredentialsException,
    OrganizationStatusException,
    PasswordPolicyException,
    PasswordResetException,
    RegistrationException,
    VerificationException,
)
from core.exceptions.base import AuthenticationError, BusinessRuleError, ConflictError, ValidationError


class TestExceptionInheritance:
    """Exception hierarchy structure tests."""

    def test_base_exception_is_authentication_error(self) -> None:
        assert issubclass(AuthenticationException, AuthenticationError)

    def test_invalid_credentials_inherits(self) -> None:
        assert issubclass(InvalidCredentialsException, AuthenticationException)

    def test_account_locked_inherits(self) -> None:
        assert issubclass(AccountLockedException, AuthenticationException)

    def test_email_not_verified_inherits(self) -> None:
        assert issubclass(EmailNotVerifiedException, AuthenticationException)

    def test_duplicate_email_inherits_conflict(self) -> None:
        assert issubclass(DuplicateEmailException, ConflictError)

    def test_duplicate_username_inherits_conflict(self) -> None:
        assert issubclass(DuplicateUsernameException, ConflictError)

    def test_duplicate_org_inherits_conflict(self) -> None:
        assert issubclass(DuplicateOrganizationException, ConflictError)

    def test_password_policy_inherits_validation(self) -> None:
        assert issubclass(PasswordPolicyException, ValidationError)

    def test_registration_inherits(self) -> None:
        assert issubclass(RegistrationException, AuthenticationException)

    def test_password_reset_inherits(self) -> None:
        assert issubclass(PasswordResetException, AuthenticationException)

    def test_verification_inherits(self) -> None:
        assert issubclass(VerificationException, AuthenticationException)

    def test_account_status_inherits(self) -> None:
        assert issubclass(AccountStatusException, AuthenticationException)

    def test_org_status_inherits(self) -> None:
        assert issubclass(OrganizationStatusException, AuthenticationException)

    def test_business_rule_inherits(self) -> None:
        assert issubclass(BusinessRuleException, BusinessRuleError)


class TestExceptionDefaults:
    """Exception default message and code tests."""

    def test_invalid_credentials_defaults(self) -> None:
        exc = InvalidCredentialsException()
        assert exc.message == InvalidCredentialsException.default_message
        assert exc.code == "INVALID_CREDENTIALS"

    def test_account_locked_defaults(self) -> None:
        exc = AccountLockedException()
        assert exc.code == "ACCOUNT_LOCKED"

    def test_email_not_verified_defaults(self) -> None:
        exc = EmailNotVerifiedException()
        assert exc.code == "EMAIL_NOT_VERIFIED"

    def test_duplicate_email_defaults(self) -> None:
        exc = DuplicateEmailException()
        assert exc.code == "DUPLICATE_EMAIL"

    def test_password_policy_defaults(self) -> None:
        exc = PasswordPolicyException()
        assert exc.code == "PASSWORD_POLICY_ERROR"

    def test_custom_message_overrides_default(self) -> None:
        exc = InvalidCredentialsException(message="Custom message")
        assert exc.message == "Custom message"

    def test_custom_details(self) -> None:
        exc = AccountLockedException(details={"locked_until": "2025-01-01"})
        assert exc.details["locked_until"] == "2025-01-01"

    def test_to_dict_serialization(self) -> None:
        exc = InvalidCredentialsException(details={"field": "password"})
        d = exc.to_dict()
        assert d["code"] == "INVALID_CREDENTIALS"
        assert d["message"] == InvalidCredentialsException.default_message
        assert d["details"]["field"] == "password"
