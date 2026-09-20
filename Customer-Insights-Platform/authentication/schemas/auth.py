"""Pydantic schemas for authentication workflows."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from authentication.helpers.normalization import normalize_email, normalize_username
from authentication.validators.inputs import (
    validate_avatar_url,
    validate_organization_name,
    validate_phone_number,
    validate_username,
)


class AuthSchema(BaseModel):
    """Base schema config."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class UserProfileInput(AuthSchema):
    """User profile fields accepted during registration or profile updates."""

    full_name: str = Field(min_length=1, max_length=200)
    display_name: str | None = Field(default=None, max_length=200)
    avatar_url: str | None = Field(default=None, max_length=512)
    time_zone: str = Field(default="UTC", max_length=64)
    language: str = Field(default="en", max_length=16)
    country: str | None = Field(default=None, min_length=2, max_length=2)
    phone: str | None = Field(default=None, max_length=32)
    department: str | None = Field(default=None, max_length=100)
    job_title: str | None = Field(default=None, max_length=100)
    preferences: dict[str, Any] = Field(default_factory=dict)
    notification_settings: dict[str, Any] = Field(default_factory=dict)
    theme: str = Field(default="light", max_length=20)

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, value: str | None) -> str | None:
        return validate_phone_number(value)

    @field_validator("avatar_url")
    @classmethod
    def _validate_avatar(cls, value: str | None) -> str | None:
        return validate_avatar_url(value)


class RegisterOrganizationRequest(AuthSchema):
    """Register a new organization and owner user."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=256)
    username: str | None = None
    organization_name: str = Field(min_length=2, max_length=255)
    organization_slug: str | None = Field(default=None, max_length=100)
    profile: UserProfileInput
    marketing_consent: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: EmailStr) -> str:
        return normalize_email(str(value))

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str | None) -> str | None:
        return normalize_username(validate_username(value))

    @field_validator("organization_name")
    @classmethod
    def _validate_org_name(cls, value: str) -> str:
        return validate_organization_name(value)


class RegisterUserRequest(AuthSchema):
    """Register a user into an existing organization."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=256)
    organization_id: uuid.UUID | None = None
    organization_slug: str | None = None
    username: str | None = None
    role_name: str = Field(default="Member", max_length=100)
    profile: UserProfileInput
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _require_org_reference(self) -> "RegisterUserRequest":
        if self.organization_id is None and not self.organization_slug:
            raise ValueError("organization_id or organization_slug is required.")
        return self

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: EmailStr) -> str:
        return normalize_email(str(value))

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str | None) -> str | None:
        return normalize_username(validate_username(value))


class RegistrationResponse(AuthSchema):
    """Registration outcome."""

    user_id: uuid.UUID
    organization_id: uuid.UUID
    workspace_id: uuid.UUID | None = None
    email: str
    status: str
    verification_required: bool


class LoginRequest(AuthSchema):
    """Enterprise login request."""

    identifier: str = Field(min_length=3, max_length=320, description="Email or username.")
    password: str = Field(min_length=1, max_length=256)
    organization_id: uuid.UUID | None = None
    organization_slug: str | None = None
    remember_me: bool = False
    device_fingerprint: str | None = Field(default=None, max_length=128)
    device_name: str | None = Field(default=None, max_length=255)
    ip_address: str | None = None
    user_agent: str | None = None


class SessionInfo(AuthSchema):
    """Authenticated session metadata."""

    session_token: str
    expires_at: datetime
    user_id: uuid.UUID
    organization_id: uuid.UUID | None
    remember_me: bool


class LoginResponse(AuthSchema):
    """Login outcome."""

    session: SessionInfo
    email: str
    username: str | None = None
    status: str


class LogoutRequest(AuthSchema):
    """Logout request."""

    session_token: str = Field(min_length=16)


class ForgotPasswordRequest(AuthSchema):
    """Forgot password request. Response is always generic."""

    email: EmailStr
    ip_address: str | None = None
    user_agent: str | None = None

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: EmailStr) -> str:
        return normalize_email(str(value))


class PasswordResetRequest(AuthSchema):
    """Complete password reset with a one-time token."""

    token: str = Field(min_length=16)
    password: str = Field(min_length=1, max_length=256)
    password_confirmation: str = Field(min_length=1, max_length=256)

    @model_validator(mode="after")
    def _passwords_match(self) -> "PasswordResetRequest":
        if self.password != self.password_confirmation:
            raise ValueError("Passwords do not match.")
        return self


class PasswordChangeRequest(AuthSchema):
    """Authenticated password change."""

    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=1, max_length=256)
    new_password_confirmation: str = Field(min_length=1, max_length=256)

    @model_validator(mode="after")
    def _passwords_match(self) -> "PasswordChangeRequest":
        if self.new_password != self.new_password_confirmation:
            raise ValueError("Passwords do not match.")
        return self


class PasswordResetResponse(AuthSchema):
    """Generic password reset response."""

    accepted: bool = True
    message: str = "If an account exists for this email, reset instructions will be sent."


class EmailVerificationRequest(AuthSchema):
    """Email verification token request."""

    token: str = Field(min_length=16)
