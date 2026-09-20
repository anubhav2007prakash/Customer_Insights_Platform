"""File storage models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import TenantModel
from database.enums import FileCategory


class FileUpload(TenantModel):
    """Central file registry."""

    __tablename__ = "file_uploads"

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(127), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(30), default="local")
    category: Mapped[FileCategory] = mapped_column(default=FileCategory.UPLOAD, index=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64))
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Document(TenantModel):
    """Business documents."""

    __tablename__ = "documents"

    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("file_uploads.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50))
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(index=True)


class Image(TenantModel):
    """Image assets."""

    __tablename__ = "images"

    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("file_uploads.id", ondelete="CASCADE"), index=True)
    alt_text: Mapped[Optional[str]] = mapped_column(String(255))
    width: Mapped[Optional[int]] = mapped_column()
    height: Mapped[Optional[int]] = mapped_column()


class AIFile(TenantModel):
    """Files used by AI pipelines."""

    __tablename__ = "ai_files"

    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("file_uploads.id", ondelete="CASCADE"), index=True)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    processing_status: Mapped[str] = mapped_column(String(30), default="pending")
    chunk_count: Mapped[int] = mapped_column(default=0)


class TempFile(TenantModel):
    """Temporary upload staging."""

    __tablename__ = "temp_files"

    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("file_uploads.id", ondelete="CASCADE"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class FileExport(TenantModel):
    """Generated export files."""

    __tablename__ = "file_exports"

    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("file_uploads.id", ondelete="CASCADE"), index=True)
    export_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_entity: Mapped[Optional[str]] = mapped_column(String(50))
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column()
