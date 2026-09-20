"""Razorpay billing custom exceptions."""
from __future__ import annotations


class RazorpayBillingError(Exception):
    """Base Razorpay billing error."""


class RazorpayConnectionError(RazorpayBillingError):
    """Raised when Razorpay cannot be reached."""


class RazorpayValidationError(RazorpayBillingError):
    """Raised when Razorpay payloads fail validation."""


class RazorpayWebhookError(RazorpayBillingError):
    """Raised when webhook processing fails."""
