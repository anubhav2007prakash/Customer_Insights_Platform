"""SQLAlchemy models for ingestion history and audit."""
from __future__ import annotations

from typing import Any, Dict, Optional
from sqlalchemy import String, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TenantModel


class ImportJob(TenantModel):
    __tablename__ = "ingestion_import_jobs"

    file_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    record_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    success_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    failed_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    metadata_: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)


class ImportRowError(TenantModel):
    __tablename__ = "ingestion_import_row_errors"

    import_job_id: Mapped[Any] = mapped_column(ForeignKey("ingestion_import_jobs.id", ondelete="CASCADE"))
    row_index: Mapped[int] = mapped_column(Integer, nullable=False)
    row_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    errors: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)


class ImportAuditLog(TenantModel):
    __tablename__ = "ingestion_audit_logs"

    import_job_id: Mapped[Any] = mapped_column(ForeignKey("ingestion_import_jobs.id", ondelete="CASCADE"))
    event: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
