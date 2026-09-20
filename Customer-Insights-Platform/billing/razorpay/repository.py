"""Razorpay repository for persistence operations."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from database.session import SessionLocal
from database.models.payment_gateway import (
    PaymentAttempt,
    PaymentAuditLog,
    PaymentTransaction,
    PaymentWebhook,
    RazorpayCustomer,
    RazorpayOrder,
    RazorpayPayment,
    RazorpayRefund,
    RazorpaySubscription,
)


class RazorpayRepository:
    def __init__(self, session=None):
        self.session = session or SessionLocal()
        self._own = session is None

    def get_customer_by_email(self, organization_id, email: str) -> Optional[RazorpayCustomer]:
        return self.session.scalars(
            select(RazorpayCustomer).where(
                RazorpayCustomer.organization_id == organization_id,
                RazorpayCustomer.email == email,
            )
        ).first()

    def add_customer(self, customer: RazorpayCustomer) -> RazorpayCustomer:
        self.session.add(customer)
        self.session.flush()
        return customer

    def get_order_by_receipt(self, organization_id, receipt_id: str) -> Optional[RazorpayOrder]:
        return self.session.scalars(
            select(RazorpayOrder).where(
                RazorpayOrder.organization_id == organization_id,
                RazorpayOrder.receipt_id == receipt_id,
            )
        ).first()

    def add_order(self, order: RazorpayOrder) -> RazorpayOrder:
        self.session.add(order)
        self.session.flush()
        return order

    def get_payment_by_provider_id(self, provider_payment_id: str) -> Optional[RazorpayPayment]:
        return self.session.scalars(
            select(RazorpayPayment).where(RazorpayPayment.razorpay_payment_id == provider_payment_id)
        ).first()

    def add_payment(self, payment: RazorpayPayment) -> RazorpayPayment:
        self.session.add(payment)
        self.session.flush()
        return payment

    def add_subscription(self, subscription: RazorpaySubscription) -> RazorpaySubscription:
        self.session.add(subscription)
        self.session.flush()
        return subscription

    def add_refund(self, refund: RazorpayRefund) -> RazorpayRefund:
        self.session.add(refund)
        self.session.flush()
        return refund

    def add_transaction(self, transaction: PaymentTransaction) -> PaymentTransaction:
        self.session.add(transaction)
        self.session.flush()
        return transaction

    def add_attempt(self, attempt: PaymentAttempt) -> PaymentAttempt:
        self.session.add(attempt)
        self.session.flush()
        return attempt

    def add_webhook(self, webhook: PaymentWebhook) -> PaymentWebhook:
        self.session.add(webhook)
        self.session.flush()
        return webhook

    def add_audit(self, audit: PaymentAuditLog) -> PaymentAuditLog:
        self.session.add(audit)
        self.session.flush()
        return audit

    def close(self):
        if self._own:
            self.session.close()
