"""Payment gateway models for Razorpay and future providers."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import PaymentStatus


class RazorpayCustomer(TenantModel):
    __tablename__ = "razorpay_customers"

    razorpay_customer_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32))
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    organization = relationship("Organization")


class RazorpayOrder(TenantModel):
    __tablename__ = "razorpay_orders"
    __table_args__ = (UniqueConstraint("organization_id", "receipt_id", name="uq_razorpay_orders_org_receipt"),)

    razorpay_order_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    status: Mapped[str] = mapped_column(String(50), default="created", index=True)
    receipt_id: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    payments: Mapped[list["RazorpayPayment"]] = relationship(back_populates="order")


class RazorpayPayment(TenantModel):
    __tablename__ = "razorpay_payments"

    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("razorpay_orders.id", ondelete="SET NULL"), index=True)
    razorpay_payment_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    status: Mapped[PaymentStatus] = mapped_column(default=PaymentStatus.PENDING, index=True)
    method: Mapped[Optional[str]] = mapped_column(String(50))
    captured: Mapped[bool] = mapped_column(Boolean, default=False)
    email: Mapped[Optional[str]] = mapped_column(String(320))
    contact: Mapped[Optional[str]] = mapped_column(String(32))
    description: Mapped[Optional[str]] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    order: Mapped[Optional["RazorpayOrder"]] = relationship(back_populates="payments")


class RazorpaySubscription(TenantModel):
    __tablename__ = "razorpay_subscriptions"

    razorpay_subscription_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("subscription_plans.id", ondelete="SET NULL"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="created", index=True)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    plan = relationship("SubscriptionPlan")


class RazorpayRefund(TenantModel):
    __tablename__ = "razorpay_refunds"

    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("razorpay_payments.id", ondelete="CASCADE"), index=True)
    razorpay_refund_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="created", index=True)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    payment: Mapped["RazorpayPayment"] = relationship()


class PaymentTransaction(TenantModel):
    __tablename__ = "payment_transactions"

    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    status: Mapped[PaymentStatus] = mapped_column(default=PaymentStatus.PENDING, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class PaymentAttempt(TenantModel):
    __tablename__ = "payment_attempts"

    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payment_transactions.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class PaymentWebhook(TenantModel):
    __tablename__ = "payment_webhooks"

    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_event_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)


class PaymentAuditLog(TenantModel):
    __tablename__ = "payment_audit_logs"

    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
