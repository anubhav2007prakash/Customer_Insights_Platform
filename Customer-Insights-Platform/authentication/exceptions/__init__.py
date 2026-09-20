"""Authentication exception hierarchy."""

from __future__ import annotations

from core.exceptions.base import AuthenticationError, BusinessRuleError, ConflictError, ValidationError


class AuthenticationException(AuthenticationError):
    """Base class for authentication module errors."""

    default_code = "AUTH_ERROR"


class InvalidCredentialsException(AuthenticationException):
    default_message = "Invalid email, username, organization, or password."
    default_code = "INVALID_CREDENTIALS"


class AccountLockedException(AuthenticationException):
    default_message = "Account is temporarily locked."
    default_code = "ACCOUNT_LOCKED"


class EmailNotVerifiedException(AuthenticationException):
    default_message = "Email address has not been verified."
    default_code = "EMAIL_NOT_VERIFIED"


class DuplicateEmailException(ConflictError):
    default_message = "An account with this email already exists."
    default_code = "DUPLICATE_EMAIL"


class DuplicateUsernameException(ConflictError):
    default_message = "An account with this username already exists."
    default_code = "DUPLICATE_USERNAME"


class DuplicateOrganizationException(ConflictError):
    default_message = "An organization with this slug already exists."
    default_code = "DUPLICATE_ORGANIZATION"


class PasswordPolicyException(ValidationError):
    default_message = "Password does not satisfy the configured policy."
    default_code = "PASSWORD_POLICY_ERROR"


class RegistrationException(AuthenticationException):
    default_message = "Registration failed."
    default_code = "REGISTRATION_ERROR"


class PasswordResetException(AuthenticationException):
    default_message = "Password reset failed."
    default_code = "PASSWORD_RESET_ERROR"


class VerificationException(AuthenticationException):
    default_message = "Email verification failed."
    default_code = "VERIFICATION_ERROR"


class AccountStatusException(AuthenticationException):
    default_message = "Account status does not allow authentication."
    default_code = "ACCOUNT_STATUS_ERROR"


class OrganizationStatusException(AuthenticationException):
    default_message = "Organization status does not allow authentication."
    default_code = "ORGANIZATION_STATUS_ERROR"


class BusinessRuleException(BusinessRuleError):
    default_message = "Authentication business rule violation."
    default_code = "AUTH_BUSINESS_RULE_ERROR"


__all__ = [
    "AccountLockedException",
    "AccountStatusException",
    "AuthenticationException",
    "BusinessRuleException",
    "DuplicateEmailException",
    "DuplicateOrganizationException",
    "DuplicateUsernameException",
    "EmailNotVerifiedException",
    "InvalidCredentialsException",
    "OrganizationStatusException",
    "PasswordPolicyException",
    "PasswordResetException",
    "RegistrationException",
    "VerificationException",
]
