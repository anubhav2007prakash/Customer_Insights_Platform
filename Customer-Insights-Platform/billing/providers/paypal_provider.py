"""PayPal payment provider adapter."""
from __future__ import annotations

from typing import Any

from billing.providers.base_provider import PaymentProvider


class PayPalProvider(PaymentProvider):
    def create_customer(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("PayPal customer creation not implemented yet")

    def create_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("PayPal order creation not implemented yet")

    def create_subscription(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("PayPal subscription creation not implemented yet")

    def capture_payment(self, payment_id: str, amount: int | None = None) -> dict[str, Any]:
        raise NotImplementedError("PayPal capture payment not implemented yet")

    def verify_signature(self, signature: str, payload: bytes, secret: str) -> dict[str, Any]:
        raise NotImplementedError("PayPal signature verification not implemented yet")

    def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        raise NotImplementedError("PayPal cancel subscription not implemented yet")

    def pause_subscription(self, subscription_id: str) -> dict[str, Any]:
        raise NotImplementedError("PayPal pause subscription not implemented yet")

    def resume_subscription(self, subscription_id: str) -> dict[str, Any]:
        raise NotImplementedError("PayPal resume subscription not implemented yet")

    def create_refund(self, payment_id: str, amount: int | None = None, reason: str | None = None) -> dict[str, Any]:
        raise NotImplementedError("PayPal refund not implemented yet")

    def get_payment_status(self, payment_id: str) -> dict[str, Any]:
        raise NotImplementedError("PayPal get payment status not implemented yet")
