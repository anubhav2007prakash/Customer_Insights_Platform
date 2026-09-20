"""Repository helpers for ingestion models."""
from __future__ import annotations

from typing import Optional, List, Dict, Any
from sqlalchemy import select
from database.session import SessionLocal

from ingestion.repositories.models import ImportJob, ImportRowError, ImportAuditLog


class IngestionRepository:
    def __init__(self, session=None):
        self.session = session or SessionLocal()
        self._own = session is None

    def create_job(self, organization_id, **kwargs) -> ImportJob:
        # translate metadata -> metadata_ if present
        if "metadata" in kwargs and "metadata_" not in kwargs:
            kwargs["metadata_"] = kwargs.pop("metadata")
        job = ImportJob(organization_id=organization_id, **kwargs)
        self.session.add(job)
        self.session.flush()
        return job

    def update_job_counts(self, job: ImportJob, success: int = 0, failed: int = 0, record_count: int = 0):
        job.success_count = (job.success_count or 0) + success
        job.failed_count = (job.failed_count or 0) + failed
        job.record_count = (job.record_count or 0) + record_count
        self.session.flush()
        return job

    def add_row_error(self, job: ImportJob, row_index: int, row: Dict[str, Any], errors: Dict[str, Any]) -> ImportRowError:
        r = ImportRowError(import_job_id=job.id, row_index=row_index, row_data=row, errors=errors, organization_id=job.organization_id)
        self.session.add(r)
        self.session.flush()
        return r

    def add_audit(self, job: ImportJob, event: str, details: Dict[str, Any], user_id: Optional[str] = None) -> ImportAuditLog:
        a = ImportAuditLog(import_job_id=job.id, event=event, details=details or {}, user_id=user_id, organization_id=job.organization_id)
        self.session.add(a)
        self.session.flush()
        return a

    def close(self):
        if self._own:
            self.session.close()
