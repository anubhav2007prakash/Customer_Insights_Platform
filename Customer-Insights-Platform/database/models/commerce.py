"""Commerce and transaction models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import InvoiceStatus, OrderStatus, PaymentStatus


class ProductCategory(TenantModel):
    """Product category hierarchy."""

    __tablename__ = "product_categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("product_categories.id", ondelete="SET NULL"))
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)


class Product(TenantModel):
    """Product catalog."""

    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("organization_id", "sku", name="uq_products_org_sku"),)

    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("product_categories.id", ondelete="SET NULL"))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class Order(TenantModel):
    """Customer orders."""

    __tablename__ = "orders"
    __table_args__ = (UniqueConstraint("organization_id", "order_number", name="uq_orders_org_number"),)

    order_number: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.PENDING, index=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    discount_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    tax_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    shipping_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Line items on an order."""

    __tablename__ = "order_items"

    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")


class Invoice(TenantModel):
    """Billing invoices."""

    __tablename__ = "invoices"
    __table_args__ = (UniqueConstraint("organization_id", "invoice_number", name="uq_invoices_org_number"),)

    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"))
    status: Mapped[InvoiceStatus] = mapped_column(default=InvoiceStatus.DRAFT, index=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    tax_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class InvoiceItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Invoice line items."""

    __tablename__ = "invoice_items"

    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"), index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)


class Payment(TenantModel):
    """Payment transactions."""

    __tablename__ = "payments"

    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("invoices.id", ondelete="SET NULL"), index=True)
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[PaymentStatus] = mapped_column(default=PaymentStatus.PENDING, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_payment_id: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)


class Refund(TenantModel):
    """Refund records."""

    __tablename__ = "refunds"

    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payments.id", ondelete="RESTRICT"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[PaymentStatus] = mapped_column(default=PaymentStatus.PENDING)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class CustomerSubscription(TenantModel):
    """Recurring product subscriptions."""

    __tablename__ = "customer_subscriptions"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    mrr: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Coupon(TenantModel):
    """Discount coupons."""

    __tablename__ = "coupons"
    __table_args__ = (UniqueConstraint("organization_id", "code", name="uq_coupons_org_code"),)

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)  # percent | fixed
    discount_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    max_uses: Mapped[Optional[int]] = mapped_column(Integer)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CouponRedemption(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Coupon usage tracking."""

    __tablename__ = "coupon_redemptions"

    coupon_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("coupons.id", ondelete="CASCADE"), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)


class TaxRate(TenantModel):
    """Tax rate definitions."""

    __tablename__ = "tax_rates"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    region: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ShippingRecord(TenantModel):
    """Shipping and fulfillment records."""

    __tablename__ = "shipping_records"

    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    carrier: Mapped[Optional[str]] = mapped_column(String(100))
    tracking_number: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    shipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    address: Mapped[dict] = mapped_column(JSONB, default=dict)
