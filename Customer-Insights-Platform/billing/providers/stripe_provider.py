"""Stripe payment provider adapter."""
from __future__ import annotations

from typing import Any

from billing.providers.base_provider import PaymentProvider
from billing.stripe.client import StripeClient
from billing.stripe.exceptions import StripeBillingError


class StripeProvider(PaymentProvider):
    def __init__(self, client: StripeClient | None = None):
        self.client = client or StripeClient()

    def create_customer(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.create_customer(
            email=payload["email"],
            name=payload.get("name"),
            metadata=payload.get("metadata"),
        )

    def create_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise StripeBillingError("Stripe order creation not supported by this adapter")

    def create_subscription(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.create_checkout_session(
            customer_id=payload["customer_id"],
            price_id=payload["price_id"],
            success_url=payload["success_url"],
            cancel_url=payload["cancel_url"],
            trial_days=payload.get("trial_days"),
        )

    def capture_payment(self, payment_id: str, amount: int | None = None) -> dict[str, Any]:
        return self.client.update_subscription(payment_id, invoice_now=True)

    def verify_signature(self, signature: str, payload: bytes, secret: str) -> dict[str, Any]:
        return self.client.construct_event(payload, signature, secret)

    def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        return self.client.cancel_subscription(subscription_id)

    def pause_subscription(self, subscription_id: str) -> dict[str, Any]:
        raise StripeBillingError("Stripe pause subscription must be handled in Stripe dashboard")

    def resume_subscription(self, subscription_id: str) -> dict[str, Any]:
        raise StripeBillingError("Stripe resume subscription must be handled in Stripe dashboard")

    def create_refund(self, payment_id: str, amount: int | None = None, reason: str | None = None) -> dict[str, Any]:
        raise StripeBillingError("Stripe refund is not implemented in this adapter")

    def get_payment_status(self, payment_id: str) -> dict[str, Any]:
        return self.client.retrieve_subscription(payment_id)
