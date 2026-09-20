"""Stripe client wrapper for the InsightForge AI billing integration."""
from __future__ import annotations

import importlib
import os

from billing.stripe.exceptions import StripeConnectionError


class StripeClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("STRIPE_API_KEY")
        if not self.api_key:
            raise StripeConnectionError("Stripe API key is not configured")

        try:
            stripe = importlib.import_module("stripe")
        except ModuleNotFoundError as exc:
            raise StripeConnectionError("Stripe SDK is not installed") from exc

        self.client = stripe
        self.StripeError = stripe.error.StripeError
        stripe.api_key = self.api_key

    def create_customer(self, email: str, name: str | None = None, metadata: dict | None = None) -> dict:
        try:
            customer = self.client.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {},
            )
            return customer
        except self.StripeError as exc:
            raise StripeConnectionError("Failed to create Stripe customer") from exc

    def retrieve_customer(self, customer_id: str) -> dict:
        try:
            return self.client.Customer.retrieve(customer_id)
        except self.StripeError as exc:
            raise StripeConnectionError("Failed to retrieve Stripe customer") from exc

    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription",
        trial_days: int | None = None,
        promotion_code: str | None = None,
    ) -> dict:
        params: dict[str, object] = {
            "customer": customer_id,
            "line_items": [{"price": price_id, "quantity": 1}],
            "mode": mode,
            "success_url": success_url,
            "cancel_url": cancel_url,
        }

        if trial_days:
            params["subscription_data"] = {"trial_period_days": trial_days}

        if promotion_code:
            params["allow_promotion_codes"] = True

        try:
            session = self.client.checkout.Session.create(**params)
            return session
        except self.StripeError as exc:
            raise StripeConnectionError("Failed to create Stripe checkout session") from exc

    def create_billing_portal_session(self, customer_id: str, return_url: str) -> dict:
        try:
            session = self.client.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session
        except self.StripeError as exc:
            raise StripeConnectionError("Failed to create Stripe billing portal session") from exc

    def retrieve_subscription(self, subscription_id: str) -> dict:
        try:
            return self.client.Subscription.retrieve(subscription_id)
        except self.StripeError as exc:
            raise StripeConnectionError("Failed to retrieve Stripe subscription") from exc

    def update_subscription(self, subscription_id: str, **kwargs) -> dict:
        try:
            return self.client.Subscription.modify(subscription_id, **kwargs)
        except self.StripeError as exc:
            raise StripeConnectionError("Failed to update Stripe subscription") from exc

    def cancel_subscription(self, subscription_id: str, invoice_now: bool = False) -> dict:
        try:
            return self.client.Subscription.delete(subscription_id)
        except self.StripeError as exc:
            raise StripeConnectionError("Failed to cancel Stripe subscription") from exc

    def create_promotion_code(self, coupon_id: str) -> dict:
        try:
            promotion = self.client.PromotionCode.create(coupon=coupon_id)
            return promotion
        except self.StripeError as exc:
            raise StripeConnectionError("Failed to create Stripe promotion code") from exc

    def construct_event(self, payload: bytes, sig_header: str, endpoint_secret: str) -> dict:
        try:
            return self.client.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=endpoint_secret,
            )
        except self.StripeError as exc:
            raise StripeConnectionError("Invalid Stripe webhook signature") from exc
