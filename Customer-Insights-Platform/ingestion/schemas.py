"""Pydantic schemas for ingestion APIs and reports."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class UploadResult(BaseModel):
    file_name: str
    preview: List[Dict[str, Any]]
    checksum: str


class ValidationErrorRow(BaseModel):
    row_index: int
    errors: List[str]
    row: Dict[str, Any]


class ValidationReport(BaseModel):
    total: int
    passed: int
    failed: int
    errors: List[Dict[str, Any]]
