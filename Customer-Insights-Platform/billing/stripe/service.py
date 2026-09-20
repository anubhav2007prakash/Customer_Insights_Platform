"""Stripe billing service that coordinates local subscription state and Stripe API calls."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from billing.stripe.client import StripeClient
from billing.stripe.exceptions import PaymentFailedError, SubscriptionSyncError
from billing.stripe.schemas import CheckoutSessionPayload, PortalSessionPayload
from database.models.tenant import BillingAccount, Organization, Subscription, SubscriptionPlan
from database.session import SessionLocal
from database.enums import SubscriptionStatus

logger = logging.getLogger(__name__)


class StripeBillingService:
    def __init__(self, client: StripeClient | None = None):
        self.client = client or StripeClient()

    def ensure_customer(self, db, organization: Organization, billing_email: str) -> str:
        if organization.billing_accounts and organization.billing_accounts[0].stripe_customer_id:
            return organization.billing_accounts[0].stripe_customer_id

        customer = self.client.create_customer(
            email=billing_email,
            name=organization.name,
            metadata={"organization_id": str(organization.id), "organization_slug": organization.slug},
        )

        billing_account = BillingAccount(
            organization_id=organization.id,
            stripe_customer_id=customer.id,
            billing_email=billing_email,
            currency="USD",
            address={},
        )
        db.add(billing_account)
        db.flush()

        logger.info("Created Stripe customer %s for organization %s", customer.id, organization.id)
        return customer.id

    def create_checkout_session(self, payload: CheckoutSessionPayload) -> str:
        with SessionLocal() as db:
            organization = db.get(Organization, payload.organization_id)
            if not organization:
                raise SubscriptionSyncError("Organization not found")

            customer_id = self.ensure_customer(db, organization, billing_email=organization.slug + "@example.com")
            session = self.client.create_checkout_session(
                customer_id=customer_id,
                price_id=payload.plan_price_id,
                success_url=payload.success_url,
                cancel_url=payload.cancel_url,
                mode=payload.mode,
                trial_days=payload.trial_days,
                promotion_code=payload.promotion_code,
            )

            db.commit()
            logger.info("Created checkout session for org=%s price=%s", organization.id, payload.plan_price_id)
            return session.url

    def create_billing_portal_session(self, payload: PortalSessionPayload) -> str:
        session = self.client.create_billing_portal_session(
            customer_id=payload.stripe_customer_id,
            return_url=payload.return_url,
        )

        logger.info("Created billing portal session for customer %s", payload.stripe_customer_id)
        return session.url

    def sync_subscription(self, subscription_id: str) -> Subscription:
        subscription_data = self.client.retrieve_subscription(subscription_id)
        with SessionLocal() as db:
            subscription = db.query(Subscription).filter_by(stripe_subscription_id=subscription_id).first()
            if not subscription:
                raise SubscriptionSyncError("Local subscription not found")

            subscription.status = SubscriptionStatus(subscription_data.status)
            subscription.current_period_start = datetime.fromtimestamp(subscription_data.current_period_start, tz=timezone.utc)
            subscription.current_period_end = datetime.fromtimestamp(subscription_data.current_period_end, tz=timezone.utc)
            subscription.cancel_at = (
                datetime.fromtimestamp(subscription_data.cancel_at, tz=timezone.utc)
                if subscription_data.cancel_at
                else None
            )
            db.flush()

            logger.info("Synchronized subscription %s status=%s", subscription_id, subscription.status)
            return subscription

    def cancel_subscription(self, subscription_id: str) -> dict:
        result = self.client.cancel_subscription(subscription_id)
        logger.info("Canceled Stripe subscription %s", subscription_id)
        return result

    def resume_subscription(self, subscription_id: str) -> dict:
        subscription = self.client.retrieve_subscription(subscription_id)
        if subscription.status != "canceled":
            raise SubscriptionSyncError("Subscription is not canceled")

        result = self.client.update_subscription(subscription_id, cancel_at=None)
        logger.info("Resumed Stripe subscription %s", subscription_id)
        return result

    def update_subscription_plan(self, subscription_id: str, price_id: str) -> dict:
        subscription = self.client.retrieve_subscription(subscription_id)
        item_id = self._get_subscription_item_id(subscription)
        if not item_id:
            raise SubscriptionSyncError("Subscription item id is required to update plan")

        result = self.client.update_subscription(subscription_id, items=[{"id": item_id, "price": price_id}])
        logger.info("Updated Stripe subscription %s to price %s", subscription_id, price_id)
        return result

    def _get_subscription_item_id(self, subscription_data: dict) -> str | None:
        items = getattr(subscription_data, "items", None) or subscription_data.get("items", {})
        data = getattr(items, "data", None) or items.get("data", [])
        if not data:
            return None

        first_item = data[0]
        return getattr(first_item, "id", None) or first_item.get("id")

    def handle_payment_failed(self, invoice_id: str) -> None:
        logger.warning("Payment failed for invoice %s", invoice_id)
        raise PaymentFailedError("Payment failed for invoice %s" % invoice_id)
