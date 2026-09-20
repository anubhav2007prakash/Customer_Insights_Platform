"""Razorpay payload validation helpers."""
from __future__ import annotations

from billing.razorpay.exceptions import RazorpayValidationError


def validate_webhook_payload(payload: bytes) -> dict[str, Any]:
    if not payload:
        raise RazorpayValidationError("Webhook payload is empty")

    try:
        return __import__("json").loads(payload)
    except ValueError as exc:
        raise RazorpayValidationError("Webhook payload is not valid JSON") from exc
