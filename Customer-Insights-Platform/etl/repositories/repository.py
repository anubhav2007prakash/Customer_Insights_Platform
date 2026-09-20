"""Repository for ETL persistence: jobs, runs, errors, metrics, audits."""
from __future__ import annotations

from typing import Dict, Any, Optional
from database.session import SessionLocal
from etl.repositories import models as etl_models
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


class ETLRepository:
    def __init__(self, session=None):
        self.session = session or SessionLocal()
        self._own = session is None

    def create_job(self, organization_id, **kwargs):
        job = etl_models.ETLJob(organization_id=organization_id, **kwargs)
        self.session.add(job)
        self.session.flush()
        return job

    def start_run(self, organization_id, job_id):
        run = etl_models.ETLRun(organization_id=organization_id, job_id=job_id, status="running", started_at=datetime.utcnow())
        self.session.add(run)
        self.session.flush()
        return run

    def complete_run(self, run, metrics: Dict[str, Any]):
        run.status = "completed"
        run.completed_at = datetime.utcnow()
        self.session.flush()
        # store metrics
        m = etl_models.ETLMetric(organization_id=run.organization_id, run_id=run.id, metrics=metrics)
        self.session.add(m)
        self.session.flush()
        return run

    def record_error(self, organization_id, run_id, record_index, error_type, details: Optional[Dict[str, Any]] = None):
        try:
            e = etl_models.ETLError(organization_id=organization_id, run_id=run_id, record_index=record_index, error_type=error_type, details=details or {})
            self.session.add(e)
            self.session.flush()
            return e
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def add_audit(self, organization_id, run_id, event: str, details: Optional[Dict[str, Any]] = None):
        a = etl_models.ETLAuditLog(organization_id=organization_id, run_id=run_id, event=event, details=details or {})
        self.session.add(a)
        self.session.flush()
        return a

    def close(self):
        if self._own:
            self.session.close()
