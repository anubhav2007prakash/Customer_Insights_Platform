"""AI and conversational intelligence models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import AIMessageRole, InsightSeverity, MLModelStatus


class AIConversation(TenantModel):
    """AI chat conversation sessions."""

    __tablename__ = "ai_conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    model_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ml_model_versions.id", ondelete="SET NULL"))
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)


class AIMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Individual messages in AI conversations."""

    __tablename__ = "ai_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[AIMessageRole] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class PromptHistory(TenantModel):
    """Historical prompts for audit and optimization."""

    __tablename__ = "prompt_history"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ai_conversations.id", ondelete="SET NULL"))
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)


class Embedding(TenantModel):
    """Vector embeddings for semantic search (pgvector column in migration)."""

    __tablename__ = "embeddings"

    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    # embedding vector stored via raw SQL / pgvector; metadata here
    chunk_text: Mapped[Optional[str]] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class KnowledgeBaseDocument(TenantModel):
    """Documents in the AI knowledge base."""

    __tablename__ = "knowledge_base_documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(512))
    file_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("file_uploads.id", ondelete="SET NULL"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)


class AIInsight(TenantModel):
    """AI-generated business insights."""

    __tablename__ = "ai_insights"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[InsightSeverity] = mapped_column(default=InsightSeverity.INFO, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50))
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class AIRecommendation(TenantModel):
    """Next-best-action recommendations."""

    __tablename__ = "ai_recommendations"

    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    impact_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)


class AIPrediction(TenantModel):
    """ML/AI prediction outputs."""

    __tablename__ = "ai_predictions"

    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    value: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    probability: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    model_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ml_model_versions.id", ondelete="RESTRICT"))
    features_used: Mapped[dict] = mapped_column(JSONB, default=dict)
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class AIForecast(TenantModel):
    """AI-generated forecasts."""

    __tablename__ = "ai_forecasts"

    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    forecast_value: Mapped[Decimal] = mapped_column(Numeric(16, 2), nullable=False)
    lower_bound: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2))
    upper_bound: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2))
    model_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ml_model_versions.id", ondelete="RESTRICT"))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AIReport(TenantModel):
    """AI-authored analytical reports."""

    __tablename__ = "ai_reports"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    generated_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AIExplanation(TenantModel):
    """Explainability records for AI decisions."""

    __tablename__ = "ai_explanations"

    prediction_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ai_predictions.id", ondelete="CASCADE"))
    insight_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ai_insights.id", ondelete="CASCADE"))
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    feature_importance: Mapped[dict] = mapped_column(JSONB, default=dict)


class VectorMetadata(TenantModel):
    """Metadata for vector store entries."""

    __tablename__ = "vector_metadata"

    embedding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("embeddings.id", ondelete="CASCADE"), index=True)
    collection: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    indexed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class MLModelVersion(TenantModel):
    """Registered ML/AI model versions."""

    __tablename__ = "ml_model_versions"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[MLModelStatus] = mapped_column(default=MLModelStatus.STAGING, index=True)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    artifact_uri: Mapped[Optional[str]] = mapped_column(String(512))
    metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    deployed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class PromptTemplate(TenantModel):
    """Reusable prompt templates."""

    __tablename__ = "prompt_templates"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[list] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
