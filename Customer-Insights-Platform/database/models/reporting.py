"""Reporting models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TenantModel, UUIDPrimaryKeyMixin, TimestampMixin, JSONB
from database.enums import ReportFormat, ReportStatus


class ReportTemplate(TenantModel):
    """Report template definitions."""

    __tablename__ = "report_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    layout: Mapped[dict] = mapped_column(JSONB, default=dict)
    default_format: Mapped[ReportFormat] = mapped_column(default=ReportFormat.PDF)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)


class Report(TenantModel):
    """Generated report instances."""

    __tablename__ = "reports"

    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("report_templates.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[ReportStatus] = mapped_column(default=ReportStatus.DRAFT, index=True)
    format: Mapped[ReportFormat] = mapped_column(default=ReportFormat.PDF)
    parameters: Mapped[dict] = mapped_column(JSONB, default=dict)
    file_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("file_uploads.id", ondelete="SET NULL"))
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)


class ScheduledReport(TenantModel):
    """Scheduled report jobs."""

    __tablename__ = "scheduled_reports"

    report_template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("report_templates.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cron_expression: Mapped[str] = mapped_column(String(100), nullable=False)
    format: Mapped[ReportFormat] = mapped_column(default=ReportFormat.PDF)
    recipients: Mapped[list] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)


class ReportExport(TenantModel):
    """Report export jobs."""

    __tablename__ = "report_exports"

    report_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    format: Mapped[ReportFormat] = mapped_column(nullable=False)
    file_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("file_uploads.id", ondelete="SET NULL"))
    status: Mapped[ReportStatus] = mapped_column(default=ReportStatus.GENERATING)
    exported_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    exported_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))


class ReportShare(TenantModel):
    """Report sharing permissions."""

    __tablename__ = "report_shares"

    report_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    shared_with_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    shared_with_email: Mapped[Optional[str]] = mapped_column(String(320))
    permission: Mapped[str] = mapped_column(String(20), default="view")
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class ReportVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Report version history."""

    __tablename__ = "report_versions"

    report_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    file_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("file_uploads.id", ondelete="SET NULL"))
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
