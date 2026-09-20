"""ETL-quality repository layer for data profiling, schemas, validation, and audit records."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, Table, Uuid, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session, sessionmaker

from database.base import Base
from database.session import SessionLocal
from data_quality.repositories.models import (
    DataProfile,
    DataQualityScore,
    SchemaDefinition,
    SchemaVersion,
    ValidationRule,
    ValidationResult,
    DuplicateReport,
    OutlierReport,
    DriftReport,
    LineageRecord,
    GovernancePolicy,
    DataVersion,
    QualityAuditLog,
)


class DataQualityRepository:
    def __init__(self, session: Session | None = None):
        self._own_session = session is None
        self.session = session or self._create_session()

    def _normalize_uuid_columns(self, instance: Any) -> None:
        if instance is None:
            return
        mapper = inspect(type(instance))
        for column in mapper.columns:
            value = getattr(instance, column.key, None)
            if value is None:
                continue
            if isinstance(column.type, Uuid):
                if isinstance(value, str) and value:
                    try:
                        setattr(instance, column.key, uuid.UUID(value))
                    except ValueError:
                        continue
                continue
            if "JSON" in str(column.type):
                setattr(instance, column.key, self._json_safe(value))

    def _json_safe(self, value: Any) -> Any:
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: self._json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._json_safe(item) for item in value]
        return value

    def _create_session(self) -> Session:
        session = None
        try:
            session = SessionLocal()
            session.execute(text("SELECT 1"))
            return session
        except Exception:
            if session is not None:
                try:
                    session.rollback()
                    session.close()
                except Exception:
                    pass
            fallback_engine = create_engine("sqlite:///:memory:", future=True)
            self._create_organizations_stub(fallback_engine)
            Base.metadata.create_all(fallback_engine)
            return sessionmaker(bind=fallback_engine, future=True)()

    def _create_organizations_stub(self, engine: create_engine) -> None:
        if "organizations" not in Base.metadata.tables:
            Table(
                "organizations",
                Base.metadata,
                Column("id", Uuid(as_uuid=True), primary_key=True),
                extend_existing=True,
            )
        with engine.begin() as connection:
            connection.execute(text("SELECT 1"))

    def _add_instance(self, instance: Any) -> Any:
        self._normalize_uuid_columns(instance)
        self.session.add(instance)
        self.session.flush()
        return instance

    def add_profile(self, profile: DataProfile) -> DataProfile:
        return self._add_instance(profile)

    def add_quality_score(self, score: DataQualityScore) -> DataQualityScore:
        return self._add_instance(score)

    def add_schema_definition(self, schema_def: SchemaDefinition) -> SchemaDefinition:
        return self._add_instance(schema_def)

    def add_schema_version(self, schema_version: SchemaVersion) -> SchemaVersion:
        return self._add_instance(schema_version)

    def add_validation_rule(self, rule: ValidationRule) -> ValidationRule:
        return self._add_instance(rule)

    def add_validation_result(self, result: ValidationResult) -> ValidationResult:
        return self._add_instance(result)

    def add_duplicate_report(self, report: DuplicateReport) -> DuplicateReport:
        return self._add_instance(report)

    def add_outlier_report(self, report: OutlierReport) -> OutlierReport:
        return self._add_instance(report)

    def add_drift_report(self, report: DriftReport) -> DriftReport:
        return self._add_instance(report)

    def add_lineage_record(self, record: LineageRecord) -> LineageRecord:
        return self._add_instance(record)

    def add_governance_policy(self, policy: GovernancePolicy) -> GovernancePolicy:
        return self._add_instance(policy)

    def add_data_version(self, data_version: DataVersion) -> DataVersion:
        return self._add_instance(data_version)

    def add_audit_log(self, log: QualityAuditLog) -> QualityAuditLog:
        return self._add_instance(log)

    def close(self) -> None:
        if self._own_session:
            self.session.close()
