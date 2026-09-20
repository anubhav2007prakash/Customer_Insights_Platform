"""InsightForge AI — Pydantic validation schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ORMSchema(BaseModel):
    """Base schema with ORM mode."""

    model_config = ConfigDict(from_attributes=True)


# ── Organization ────────────────────────────────────────────────────────────

class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    industry: Optional[str] = Field(default=None, max_length=100)
    timezone: str = Field(default="UTC", max_length=64)


class OrganizationRead(ORMSchema):
    id: uuid.UUID
    name: str
    slug: str
    status: str
    created_at: datetime


# ── User ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)


class UserRead(ORMSchema):
    id: uuid.UUID
    email: str
    status: str
    created_at: datetime


# ── Customer ──────────────────────────────────────────────────────────────────

class CustomerCreate(BaseModel):
    organization_id: uuid.UUID
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=32)
    lifecycle_stage: str = "lead"
    external_id: Optional[str] = Field(default=None, max_length=100)


class CustomerRead(ORMSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: Optional[str]
    full_name: Optional[str]
    status: str
    lifecycle_stage: str
    created_at: datetime


class CustomerScoreRead(ORMSchema):
    score_type: str
    value: Decimal
    computed_at: datetime

    @field_validator("value")
    @classmethod
    def validate_score_range(cls, v: Decimal, info) -> Decimal:
        score_type = info.data.get("score_type")
        if score_type in ("health", "engagement", "loyalty", "churn") and not (0 <= v <= 100):
            raise ValueError("Score must be between 0 and 100")
        return v


# ── Order ─────────────────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    organization_id: uuid.UUID
    customer_id: uuid.UUID
    order_number: str = Field(max_length=50)
    total: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class OrderRead(ORMSchema):
    id: uuid.UUID
    order_number: str
    status: str
    total: Decimal
    placed_at: datetime


# ── Campaign ──────────────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    channel: str
    budget: Optional[Decimal] = Field(default=None, ge=0)


# ── AI ────────────────────────────────────────────────────────────────────────

class AIConversationCreate(BaseModel):
    organization_id: uuid.UUID
    user_id: uuid.UUID
    title: Optional[str] = Field(default=None, max_length=255)


class AIMessageCreate(BaseModel):
    conversation_id: uuid.UUID
    role: str
    content: str = Field(min_length=1)


# ── Pagination ────────────────────────────────────────────────────────────────

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    pages: int
