"""Stripe billing validation helpers."""
from __future__ import annotations

import json
from typing import Any

from billing.stripe.exceptions import InvalidWebhookError


def validate_webhook_payload(payload: bytes) -> dict[str, Any]:
    try:
        data = json.loads(payload)
    except ValueError as exc:
        raise InvalidWebhookError("Invalid webhook payload") from exc

    if "type" not in data or "data" not in data:
        raise InvalidWebhookError("Webhook payload missing required fields")

    return data
