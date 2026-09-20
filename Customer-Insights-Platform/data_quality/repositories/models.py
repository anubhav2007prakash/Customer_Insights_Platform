"""SQLAlchemy models for Data Quality and schema governance."""
from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, JSON, Column, DateTime, Boolean, Float, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from database.base import TenantModel


class DataProfile(TenantModel):
    __tablename__ = "data_profiles"

    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_columns: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    profile_metrics: Mapped[dict] = mapped_column(JSON, nullable=False, default={})
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DataQualityScore(TenantModel):
    __tablename__ = "data_quality_scores"

    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    category_scores: Mapped[dict] = mapped_column(JSON, nullable=False)
    grade: Mapped[str] = mapped_column(String(2), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SchemaDefinition(TenantModel):
    __tablename__ = "schema_definitions"

    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    version_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    schema_spec: Mapped[dict] = mapped_column(JSON, nullable=False)
    manual_overrides: Mapped[dict] = mapped_column(JSON, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SchemaVersion(TenantModel):
    __tablename__ = "schema_versions"

    schema_definition_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    change_summary: Mapped[str] = mapped_column(Text, nullable=True)
    schema_spec: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ValidationRule(TenantModel):
    __tablename__ = "validation_rules"

    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    rule_name: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(100), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ValidationResult(TenantModel):
    __tablename__ = "validation_results"

    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    rule_name: Mapped[str] = mapped_column(String(200), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DuplicateReport(TenantModel):
    __tablename__ = "duplicate_reports"

    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    report: Mapped[dict] = mapped_column(JSON, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OutlierReport(TenantModel):
    __tablename__ = "outlier_reports"

    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    report: Mapped[dict] = mapped_column(JSON, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DriftReport(TenantModel):
    __tablename__ = "drift_reports"

    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    baseline_version: Mapped[int] = mapped_column(Integer, nullable=False)
    target_version: Mapped[int] = mapped_column(Integer, nullable=False)
    drift_metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LineageRecord(TenantModel):
    __tablename__ = "lineage_records"

    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    lineage: Mapped[dict] = mapped_column(JSON, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class GovernancePolicy(TenantModel):
    __tablename__ = "governance_policies"

    policy_name: Mapped[str] = mapped_column(String(200), nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    policy_type: Mapped[str] = mapped_column(String(100), nullable=False)
    policy_definition: Mapped[dict] = mapped_column(JSON, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DataVersion(TenantModel):
    __tablename__ = "data_versions"

    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    import_version: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    transformation_version: Mapped[int] = mapped_column(Integer, nullable=False)
    validation_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class QualityAuditLog(TenantModel):
    __tablename__ = "quality_audit_logs"

    event: Mapped[str] = mapped_column(String(200), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
