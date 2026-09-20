"""Razorpay payment provider adapter."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from billing.providers.base_provider import PaymentProvider
from billing.razorpay.client import RazorpayClient
from billing.razorpay.exceptions import RazorpayBillingError


class RazorpayProvider(PaymentProvider):
    def __init__(self, client: RazorpayClient | None = None):
        self.client = client or RazorpayClient()

    def create_customer(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.create_customer(
            name=payload.get("name"),
            email=payload["email"],
            contact=payload.get("phone"),
            company_name=payload.get("company_name"),
            metadata=payload.get("metadata", {}),
        )

    def create_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.create_order(
            amount=int(Decimal(payload["amount"]) * 100),
            currency=payload.get("currency", "INR"),
            receipt=payload["receipt"],
            notes=payload.get("metadata", {}),
        )

    def create_subscription(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.create_subscription(
            customer_id=payload["customer_id"],
            plan_id=payload["plan_id"],
            total_count=payload.get("total_count"),
            trial_days=payload.get("trial_days"),
            start_at=payload.get("start_at"),
            notes=payload.get("metadata", {}),
        )

    def capture_payment(self, payment_id: str, amount: int | None = None) -> dict[str, Any]:
        return self.client.capture_payment(payment_id, amount)

    def verify_signature(self, signature: str, payload: bytes, secret: str) -> dict[str, Any]:
        return self.client.verify_signature(signature, payload, secret)

    def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        return self.client.cancel_subscription(subscription_id)

    def pause_subscription(self, subscription_id: str) -> dict[str, Any]:
        return self.client.pause_subscription(subscription_id)

    def resume_subscription(self, subscription_id: str) -> dict[str, Any]:
        return self.client.resume_subscription(subscription_id)

    def create_refund(self, payment_id: str, amount: int | None = None, reason: str | None = None) -> dict[str, Any]:
        return self.client.create_refund(payment_id, amount=amount, notes={"reason": reason} if reason else {})

    def get_payment_status(self, payment_id: str) -> dict[str, Any]:
        return self.client.get_payment(payment_id)
