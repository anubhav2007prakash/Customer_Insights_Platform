"""Stripe webhook processing for billing events."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from billing.stripe.client import StripeClient
from billing.stripe.exceptions import InvalidWebhookError, SubscriptionSyncError, PaymentFailedError
from billing.stripe.validators import validate_webhook_payload
from database.enums import IntegrationProvider, SubscriptionStatus
from database.models.integrations import Integration, WebhookEvent
from database.models.tenant import BillingAccount, Organization, Subscription, SubscriptionPlan
from database.session import SessionLocal

logger = logging.getLogger(__name__)


class StripeWebhookHandler:
    def __init__(self, client: StripeClient | None = None, endpoint_secret: str | None = None):
        self.client = client or StripeClient()
        self.endpoint_secret = endpoint_secret or __import__("os").getenv("STRIPE_WEBHOOK_SECRET")
        if not self.endpoint_secret:
            raise InvalidWebhookError("Stripe webhook secret is not configured")

    def process(self, payload: bytes, sig_header: str) -> dict[str, str]:
        validate_webhook_payload(payload)
        event = self.client.construct_event(payload, sig_header, self.endpoint_secret)

        with SessionLocal() as db:
            webhook_event = self._create_webhook_event(db, event)
            try:
                result = self._handle_event(db, event)
                webhook_event.status = "processed"
                webhook_event.processed_at = datetime.now(timezone.utc)
                db.commit()
                return result
            except Exception as exc:
                webhook_event.status = "failed"
                webhook_event.error_message = str(exc)
                webhook_event.processed_at = datetime.now(timezone.utc)
                db.commit()
                raise

    def _create_webhook_event(self, db, event: dict) -> WebhookEvent:
        customer_id = event["data"]["object"].get("customer")
        billing_account = db.query(BillingAccount).filter_by(stripe_customer_id=customer_id).first()
        organization = None
        integration = None
        if billing_account:
            organization = db.get(Organization, billing_account.organization_id)
            integration = (
                db.query(Integration)
                .filter_by(organization_id=billing_account.organization_id, provider=IntegrationProvider.STRIPE)
                .first()
            )

        webhook_event = WebhookEvent(
            organization_id=organization.id if organization else None,
            integration_id=integration.id if integration else None,
            event_type=event["type"],
            payload=event,
            received_at=datetime.now(timezone.utc),
            status="pending",
        )
        db.add(webhook_event)
        return webhook_event

    def _handle_event(self, db, event: dict) -> dict[str, str]:
        event_type = event["type"]
        obj = event["data"]["object"]

        if event_type == "checkout.session.completed":
            return self._handle_checkout_completed(db, obj)
        if event_type == "customer.subscription.created":
            return self._handle_subscription_created(db, obj)
        if event_type == "customer.subscription.updated":
            return self._handle_subscription_updated(db, obj)
        if event_type == "customer.subscription.deleted":
            return self._handle_subscription_deleted(db, obj)
        if event_type == "invoice.paid":
            return self._handle_invoice_paid(db, obj)
        if event_type == "invoice.payment_failed":
            return self._handle_payment_failed(db, obj)

        logger.info("Ignored Stripe event %s", event_type)
        return {"status": "ignored"}

    def _resolve_organization(self, db, customer_id: str) -> Organization | None:
        billing_account = db.query(BillingAccount).filter_by(stripe_customer_id=customer_id).first()
        if not billing_account:
            return None
        return db.get(Organization, billing_account.organization_id)

    def _handle_checkout_completed(self, db, obj: dict) -> dict[str, str]:
        customer_id = obj.get("customer")
        org = self._resolve_organization(db, customer_id)
        if not org:
            raise SubscriptionSyncError("Organization not found for checkout session")

        subscription_id = obj.get("subscription")
        if subscription_id:
            self._update_local_subscription(db, org, subscription_id)

        logger.info("Checkout session completed for org=%s", org.id)
        return {"status": "ok"}

    def _handle_subscription_created(self, db, obj: dict) -> dict[str, str]:
        customer_id = obj.get("customer")
        org = self._resolve_organization(db, customer_id)
        if not org:
            raise SubscriptionSyncError("Organization not found for subscription created")

        self._update_local_subscription(db, org, obj.get("id"))
        logger.info("Stripe subscription created for org=%s", org.id)
        return {"status": "ok"}

    def _handle_subscription_updated(self, db, obj: dict) -> dict[str, str]:
        customer_id = obj.get("customer")
        org = self._resolve_organization(db, customer_id)
        if not org:
            raise SubscriptionSyncError("Organization not found for subscription updated")

        self._update_local_subscription(db, org, obj.get("id"))
        logger.info("Stripe subscription updated for org=%s", org.id)
        return {"status": "ok"}

    def _handle_subscription_deleted(self, db, obj: dict) -> dict[str, str]:
        customer_id = obj.get("customer")
        org = self._resolve_organization(db, customer_id)
        if not org:
            raise SubscriptionSyncError("Organization not found for subscription deleted")

        local_sub = db.query(Subscription).filter_by(stripe_subscription_id=obj.get("id")).first()
        if local_sub:
            local_sub.status = SubscriptionStatus.CANCELED
            local_sub.cancel_at = datetime.fromtimestamp(obj.get("canceled_at"), tz=timezone.utc) if obj.get("canceled_at") else None
            db.flush()

        logger.info("Stripe subscription deleted for org=%s", org.id)
        return {"status": "ok"}

    def _handle_invoice_paid(self, db, obj: dict) -> dict[str, str]:
        subscription_id = obj.get("subscription")
        if not subscription_id:
            raise SubscriptionSyncError("Invoice paid event missing subscription")

        local_sub = db.query(Subscription).filter_by(stripe_subscription_id=subscription_id).first()
        if local_sub:
            local_sub.status = SubscriptionStatus.ACTIVE
            db.flush()

        logger.info("Invoice paid for subscription %s", subscription_id)
        return {"status": "ok"}

    def _handle_payment_failed(self, db, obj: dict) -> dict[str, str]:
        invoice_id = obj.get("id")
        logger.warning("Stripe payment failed invoice=%s", invoice_id)
        raise PaymentFailedError("Payment failed for invoice %s" % invoice_id)

    def _update_local_subscription(self, db, org: Organization, stripe_subscription_id: str) -> None:
        subscription_data = self.client.retrieve_subscription(stripe_subscription_id)
        plan = self._resolve_subscription_plan(db, subscription_data)

        local_sub = db.query(Subscription).filter_by(organization_id=org.id).first()
        if not local_sub:
            local_sub = Subscription(
                organization_id=org.id,
                plan_id=plan.id if plan else None,
                stripe_subscription_id=stripe_subscription_id,
                status=SubscriptionStatus(subscription_data.status),
                current_period_start=datetime.fromtimestamp(subscription_data.current_period_start, tz=timezone.utc),
                current_period_end=datetime.fromtimestamp(subscription_data.current_period_end, tz=timezone.utc),
                cancel_at=(datetime.fromtimestamp(subscription_data.cancel_at, tz=timezone.utc) if subscription_data.cancel_at else None),
            )
            db.add(local_sub)
        else:
            local_sub.status = SubscriptionStatus(subscription_data.status)
            local_sub.stripe_subscription_id = stripe_subscription_id
            local_sub.plan_id = plan.id if plan else local_sub.plan_id
            local_sub.current_period_start = datetime.fromtimestamp(subscription_data.current_period_start, tz=timezone.utc)
            local_sub.current_period_end = datetime.fromtimestamp(subscription_data.current_period_end, tz=timezone.utc)
            local_sub.cancel_at = (datetime.fromtimestamp(subscription_data.cancel_at, tz=timezone.utc) if subscription_data.cancel_at else None)
        db.flush()

    def _resolve_subscription_plan(self, db, subscription_data: dict) -> SubscriptionPlan | None:
        price = getattr(subscription_data.items.data[0], "price", None) if getattr(subscription_data, "items", None) else None
        if not price:
            items = subscription_data.get("items", {}) if isinstance(subscription_data, dict) else {}
            price = items.get("data", [])[0].get("price") if items.get("data") else None

        if not price:
            return None

        price_id = getattr(price, "id", None) or price.get("id")
        product_id = getattr(price, "product", None) or price.get("product")

        if price_id:
            plan = db.query(SubscriptionPlan).filter_by(stripe_price_id=price_id).first()
            if plan:
                return plan

        if product_id:
            return db.query(SubscriptionPlan).filter_by(stripe_product_id=product_id).first()

        return None
