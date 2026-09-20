"""Pydantic schemas for Stripe billing integration."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class StripeCustomerCreatePayload(BaseModel):
    organization_id: str
    email: str
    name: Optional[str]
    metadata: dict[str, Any] = Field(default_factory=dict)


class CheckoutSessionPayload(BaseModel):
    organization_id: str
    plan_price_id: str
    mode: str
    success_url: str
    cancel_url: str
    trial_days: Optional[int] = None
    promotion_code: Optional[str] = None


class PortalSessionPayload(BaseModel):
    stripe_customer_id: str
    return_url: str


class StripeEventPayload(BaseModel):
    id: str
    type: str
    data: dict[str, Any]
    created: datetime
