"""Machine learning infrastructure models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import MLModelStatus


class MLTrainingDataset(TenantModel):
    """Registered training datasets."""

    __tablename__ = "ml_training_datasets"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_query: Mapped[Optional[str]] = mapped_column(Text)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    feature_columns: Mapped[list] = mapped_column(JSONB, default=list)
    target_column: Mapped[Optional[str]] = mapped_column(String(100))
    storage_uri: Mapped[Optional[str]] = mapped_column(String(512))


class MLInferenceLog(TenantModel):
    """Inference request/response logs."""

    __tablename__ = "ml_inference_logs"

    model_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ml_model_versions.id", ondelete="RESTRICT"), index=True)
    input_features: Mapped[dict] = mapped_column(JSONB, nullable=False)
    output: Mapped[dict] = mapped_column(JSONB, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    inferred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class MLPredictionResult(TenantModel):
    """Stored prediction results for audit."""

    __tablename__ = "ml_prediction_results"

    model_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ml_model_versions.id", ondelete="RESTRICT"), index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    prediction: Mapped[dict] = mapped_column(JSONB, nullable=False)
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class FeatureStoreEntry(TenantModel):
    """Feature store values."""

    __tablename__ = "feature_store_entries"

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    feature_set: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    features: Mapped[dict] = mapped_column(JSONB, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class FeatureMetadata(TenantModel):
    """Feature definitions and lineage."""

    __tablename__ = "feature_metadata"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    data_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(255))
    transformation: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class MLModel(TenantModel):
    """ML model registry entries."""

    __tablename__ = "ml_models"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    current_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ml_model_versions.id", ondelete="SET NULL"))
    tags: Mapped[list] = mapped_column(JSONB, default=list)


class MLExperiment(TenantModel):
    """ML experiment tracking."""

    __tablename__ = "ml_experiments"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ml_models.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="running", index=True)
    hyperparameters: Mapped[dict] = mapped_column(JSONB, default=dict)
    dataset_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ml_training_datasets.id", ondelete="SET NULL"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class MLEvaluationMetric(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Model evaluation metrics."""

    __tablename__ = "ml_evaluation_metrics"

    experiment_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ml_experiments.id", ondelete="CASCADE"), index=True)
    model_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ml_model_versions.id", ondelete="CASCADE"), index=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    dataset_split: Mapped[str] = mapped_column(String(20), default="test")


class ModelMonitoringMetric(TenantModel):
    """Production model monitoring."""

    __tablename__ = "model_monitoring_metrics"

    model_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ml_model_versions.id", ondelete="CASCADE"), index=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class DriftDetectionLog(TenantModel):
    """Data/concept drift detection logs."""

    __tablename__ = "drift_detection_logs"

    model_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ml_model_versions.id", ondelete="CASCADE"), index=True)
    drift_type: Mapped[str] = mapped_column(String(30), nullable=False)  # data | concept | prediction
    feature_name: Mapped[Optional[str]] = mapped_column(String(100))
    drift_score: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    threshold: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    is_drift_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
