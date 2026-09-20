"""Razorpay billing service orchestrating local persistence and Razorpay operations."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from billing.razorpay.client import RazorpayClient
from billing.razorpay.exceptions import RazorpayBillingError, RazorpayValidationError, RazorpayWebhookError
from billing.razorpay.repository import RazorpayRepository
from billing.razorpay.schemas import (
    RazorpayCustomerPayload,
    RazorpayOrderPayload,
    RazorpayPaymentVerificationPayload,
    RazorpayRefundPayload,
    RazorpaySubscriptionPayload,
)
from billing.razorpay.validators import validate_webhook_payload
from database.enums import PaymentStatus
from database.models.payment_gateway import (
    PaymentAuditLog,
    PaymentAttempt,
    PaymentTransaction,
    PaymentWebhook,
    RazorpayCustomer,
    RazorpayOrder,
    RazorpayPayment,
    RazorpayRefund,
    RazorpaySubscription,
)
from database.models.tenant import Organization, SubscriptionPlan
from database.session import SessionLocal


class RazorpayService:
    def __init__(self, client: RazorpayClient | None = None, repo: RazorpayRepository | None = None):
        self.client = client or RazorpayClient()
        self.repo = repo or RazorpayRepository()

    def create_customer(self, payload: RazorpayCustomerPayload) -> RazorpayCustomer:
        existing = self.repo.get_customer_by_email(payload.organization_id, payload.email)
        if existing:
            return existing

        razorpay_customer = self.client.create_customer(
            name=payload.company_name or payload.email,
            email=payload.email,
            contact=payload.phone,
            company_name=payload.company_name,
            metadata=payload.metadata,
        )

        return self.repo.add_customer(
            RazorpayCustomer(
                organization_id=payload.organization_id,
                razorpay_customer_id=razorpay_customer["id"],
                email=payload.email,
                phone=payload.phone,
                company_name=payload.company_name,
                metadata_=payload.metadata,
                status=razorpay_customer.get("status", "active"),
            )
        )

    def create_order(self, payload: RazorpayOrderPayload) -> RazorpayOrder:
        existing = self.repo.get_order_by_receipt(payload.organization_id, payload.receipt)
        if existing:
            return existing

        razorpay_order = self.client.create_order(
            amount=payload.amount,
            currency=payload.currency,
            receipt=payload.receipt,
            notes=payload.metadata,
        )

        return self.repo.add_order(
            RazorpayOrder(
                organization_id=payload.organization_id,
                razorpay_order_id=razorpay_order["id"],
                amount=Decimal(razorpay_order["amount"]) / Decimal(100),
                currency=razorpay_order["currency"],
                status=razorpay_order["status"],
                receipt_id=razorpay_order["receipt"],
                payment_method=None,
                metadata_=payload.metadata,
                expires_at=(datetime.fromtimestamp(razorpay_order["expires_at"], tz=timezone.utc) if razorpay_order.get("expires_at") else None),
            )
        )

    def verify_payment(self, payload: RazorpayPaymentVerificationPayload) -> RazorpayPayment:
        try:
            self.client.verify_signature(
                payload.razorpay_signature,
                __import__("json").dumps({
                    "razorpay_payment_id": payload.razorpay_payment_id,
                    "razorpay_order_id": payload.razorpay_order_id,
                }).encode("utf-8"),
                os.getenv("RAZORPAY_WEBHOOK_SECRET", ""),
            )
        except Exception as exc:
            raise RazorpayValidationError("Payment verification failed") from exc

        payment = self.client.get_payment(payload.razorpay_payment_id)
        razorpay_payment = RazorpayPayment(
            organization_id=payload.organization_id,
            razorpay_payment_id=payload.razorpay_payment_id,
            amount=Decimal(payment["amount"]) / Decimal(100),
            currency=payment["currency"],
            status=PaymentStatus.SUCCEEDED if payment["status"] == "captured" else PaymentStatus.PENDING,
            method=payment.get("method"),
            captured=payment.get("captured", False),
            email=payment.get("email"),
            contact=payment.get("contact"),
            description=payment.get("description"),
            metadata_=payment.get("notes", {}),
        )
        return self.repo.add_payment(razorpay_payment)
