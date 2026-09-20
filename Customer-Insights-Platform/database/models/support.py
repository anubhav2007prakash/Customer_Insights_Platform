"""Customer support models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import TicketPriority, TicketStatus


class SupportTicket(TenantModel):
    """Support ticket records."""

    __tablename__ = "support_tickets"

    ticket_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[TicketStatus] = mapped_column(default=TicketStatus.OPEN, index=True)
    priority: Mapped[TicketPriority] = mapped_column(default=TicketPriority.MEDIUM, index=True)
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    category: Mapped[Optional[str]] = mapped_column(String(100))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sla_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class TicketMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Messages within a support ticket."""

    __tablename__ = "ticket_messages"

    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("support_tickets.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)


class LiveChat(TenantModel):
    """Live chat sessions."""

    __tablename__ = "live_chats"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rating: Mapped[Optional[int]] = mapped_column(Integer)


class ChatMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Messages in live chat."""

    __tablename__ = "chat_messages"

    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("live_chats.id", ondelete="CASCADE"), index=True)
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False)  # customer | agent | bot
    sender_id: Mapped[Optional[uuid.UUID]] = mapped_column()
    content: Mapped[str] = mapped_column(Text, nullable=False)


class KnowledgeBaseArticle(TenantModel):
    """Self-service knowledge base."""

    __tablename__ = "knowledge_base_articles"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))


class Feedback(TenantModel):
    """General customer feedback."""

    __tablename__ = "feedback"

    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[Optional[str]] = mapped_column(String(20))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class Rating(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Product/service ratings."""

    __tablename__ = "ratings"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[Optional[str]] = mapped_column(Text)


class Review(TenantModel):
    """Published customer reviews."""

    __tablename__ = "reviews"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)


class CSATResponse(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Customer Satisfaction survey responses."""

    __tablename__ = "csat_responses"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("support_tickets.id", ondelete="SET NULL"))
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    responded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class NPSResponse(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Net Promoter Score responses."""

    __tablename__ = "nps_responses"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)  # promoter | passive | detractor
    comment: Mapped[Optional[str]] = mapped_column(Text)
    responded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
