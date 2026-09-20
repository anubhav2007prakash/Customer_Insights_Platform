"""Stripe checkout flow integration."""
from __future__ import annotations

from billing.stripe.schemas import CheckoutSessionPayload
from billing.stripe.service import StripeBillingService


class StripeCheckoutService:
    def __init__(self, client=None):
        self.billing_service = StripeBillingService(client=client)

    def create_session(self, payload: CheckoutSessionPayload) -> str:
        return self.billing_service.create_checkout_session(payload)
