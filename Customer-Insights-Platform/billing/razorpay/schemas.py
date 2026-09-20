"""Pydantic schemas for Razorpay billing integration."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, constr


class RazorpayCustomerPayload(BaseModel):
    organization_id: constr(min_length=1)
    email: constr(min_length=1)
    phone: Optional[constr(min_length=1)]
    company_name: Optional[str]
    metadata: dict = Field(default_factory=dict)


class RazorpayOrderPayload(BaseModel):
    organization_id: constr(min_length=1)
    amount: int
    currency: constr(min_length=3, max_length=3) = "INR"
    receipt: constr(min_length=1)
    metadata: dict = Field(default_factory=dict)


class RazorpaySubscriptionPayload(BaseModel):
    organization_id: constr(min_length=1)
    customer_id: constr(min_length=1)
    plan_id: constr(min_length=1)
    total_count: Optional[int]
    trial_days: Optional[int]
    start_at: Optional[int]
    metadata: dict = Field(default_factory=dict)


class RazorpayPaymentVerificationPayload(BaseModel):
    razorpay_payment_id: constr(min_length=1)
    razorpay_order_id: constr(min_length=1)
    razorpay_signature: constr(min_length=1)


class RazorpayRefundPayload(BaseModel):
    payment_id: constr(min_length=1)
    amount: Optional[int]
    reason: Optional[str]
    metadata: dict = Field(default_factory=dict)


class RazorpayWebhookPayload(BaseModel):
    event: constr(min_length=1)
    payload: dict
    created_at: Optional[datetime]
