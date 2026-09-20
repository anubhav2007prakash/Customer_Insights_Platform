"""ETL database models for pipelines, jobs, runs, transformations, errors, metrics, and audits."""
from __future__ import annotations

from typing import Any
import uuid
from sqlalchemy import String, Integer, Text, JSON, Column
from sqlalchemy.orm import Mapped, mapped_column

from database.base import BaseModel, TenantModel


class ETLPipeline(TenantModel):
    __tablename__ = "etl_pipelines"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    config: Mapped[dict] = mapped_column(JSON, nullable=True)


class ETLJob(TenantModel):
    __tablename__ = "etl_jobs"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(nullable=True)
    trigger: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)


class ETLRun(TenantModel):
    __tablename__ = "etl_runs"

    job_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    started_at = mapped_column(nullable=True)
    completed_at = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="running")
    records_total: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    records_processed: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, nullable=True, default=0)


class ETLTransformation(TenantModel):
    __tablename__ = "etl_transformations"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    spec: Mapped[dict] = mapped_column(JSON, nullable=False)


class ETLError(TenantModel):
    __tablename__ = "etl_errors"

    run_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    record_index: Mapped[int] = mapped_column(Integer, nullable=True)
    error_type: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)


class ETLMetric(TenantModel):
    __tablename__ = "etl_metrics"

    run_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)


class ETLAuditLog(TenantModel):
    __tablename__ = "etl_audit_logs"

    run_id: Mapped[uuid.UUID] = mapped_column(nullable=True)
    event: Mapped[str] = mapped_column(String(200), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
