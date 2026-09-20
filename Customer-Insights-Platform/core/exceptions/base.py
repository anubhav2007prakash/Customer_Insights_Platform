"""Custom exception hierarchy for InsightForge AI."""

from __future__ import annotations

from typing import Any


class InsightForgeError(Exception):
    """Base exception for all application errors."""

    default_message: str = "An unexpected error occurred."
    default_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details or {}
        self.cause = cause
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for API/presentation layer."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# ── Authentication & Authorization ────────────────────────────────────────────

class AuthenticationError(InsightForgeError):
    default_message = "Authentication failed."
    default_code = "AUTHENTICATION_ERROR"


class AuthorizationError(InsightForgeError):
    default_message = "You do not have permission to perform this action."
    default_code = "AUTHORIZATION_ERROR"


class SessionExpiredError(AuthenticationError):
    default_message = "Your session has expired. Please sign in again."
    default_code = "SESSION_EXPIRED"


# ── Validation ────────────────────────────────────────────────────────────────

class ValidationError(InsightForgeError):
    default_message = "Validation failed."
    default_code = "VALIDATION_ERROR"


class NotFoundError(InsightForgeError):
    default_message = "The requested resource was not found."
    default_code = "NOT_FOUND"


class ConflictError(InsightForgeError):
    default_message = "The resource already exists or conflicts with current state."
    default_code = "CONFLICT"


# ── Infrastructure ────────────────────────────────────────────────────────────

class DatabaseError(InsightForgeError):
    default_message = "A database error occurred."
    default_code = "DATABASE_ERROR"


class ConfigurationError(InsightForgeError):
    default_message = "Application configuration is invalid."
    default_code = "CONFIGURATION_ERROR"


class CacheError(InsightForgeError):
    default_message = "Cache operation failed."
    default_code = "CACHE_ERROR"


# ── Domain-specific ───────────────────────────────────────────────────────────

class BusinessRuleError(InsightForgeError):
    default_message = "Business rule violation."
    default_code = "BUSINESS_RULE_ERROR"


class TenantError(InsightForgeError):
    default_message = "Organization context is required."
    default_code = "TENANT_ERROR"


# ── AI / ML ───────────────────────────────────────────────────────────────────

class AIError(InsightForgeError):
    default_message = "AI service error."
    default_code = "AI_ERROR"


class PredictionError(AIError):
    default_message = "Prediction failed."
    default_code = "PREDICTION_ERROR"


class ModelNotFoundError(AIError):
    default_message = "ML model not found."
    default_code = "MODEL_NOT_FOUND"


# ── Integrations & Exports ────────────────────────────────────────────────────

class IntegrationError(InsightForgeError):
    default_message = "Integration error."
    default_code = "INTEGRATION_ERROR"


class ExportError(InsightForgeError):
    default_message = "Export failed."
    default_code = "EXPORT_ERROR"


class SyncError(IntegrationError):
    default_message = "Data synchronization failed."
    default_code = "SYNC_ERROR"


# ── Files ─────────────────────────────────────────────────────────────────────

class FileValidationError(ValidationError):
    default_message = "File validation failed."
    default_code = "FILE_VALIDATION_ERROR"
