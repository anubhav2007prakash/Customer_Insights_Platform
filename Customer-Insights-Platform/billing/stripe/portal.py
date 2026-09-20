"""Stripe billing portal integration."""
from __future__ import annotations

from billing.stripe.client import StripeClient
from billing.stripe.schemas import PortalSessionPayload
from billing.stripe.exceptions import StripeConnectionError


class StripePortalService:
    def __init__(self, client: StripeClient | None = None):
        self.client = client or StripeClient()

    def create_portal_session(self, payload: PortalSessionPayload) -> str:
        session = self.client.create_billing_portal_session(
            customer_id=payload.stripe_customer_id,
            return_url=payload.return_url,
        )
        return session.url
