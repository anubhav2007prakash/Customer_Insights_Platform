"""Stripe billing custom exceptions."""

from __future__ import annotations


class StripeBillingError(Exception):
    """Base class for Stripe billing errors."""


class StripeConnectionError(StripeBillingError):
    """Raised when Stripe cannot be reached."""


class InvalidWebhookError(StripeBillingError):
    """Raised when a Stripe webhook fails validation."""


class SubscriptionSyncError(StripeBillingError):
    """Raised when subscription synchronization fails."""


class PaymentFailedError(StripeBillingError):
    """Raised when payment fails or is declined."""
