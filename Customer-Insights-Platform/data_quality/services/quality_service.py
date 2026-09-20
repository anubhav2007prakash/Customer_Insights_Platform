"""High-level orchestration service for data quality, schema, and governance."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Iterable

import pandas as pd

from data_quality.profiling.profiler import DataProfiler
from data_quality.schema.detector import SchemaDetector
from data_quality.schema.versioning import SchemaVersionManager
from data_quality.validation.validator import SchemaValidator
from data_quality.validation.rules import ValidationRuleEngine
from data_quality.scoring.scorer import QualityScorer
from data_quality.drift.detector import DriftDetector
from data_quality.lineage.tracker import LineageTracker
from data_quality.versioning.manager import VersionManager
from data_quality.repositories.repository import DataQualityRepository
from data_quality.rules.registry import rule_registry


class DataQualityService:
    def __init__(self, repository: DataQualityRepository | None = None):
        self.repository = repository or DataQualityRepository()
        self.profiler = DataProfiler()
        self.schema_detector = SchemaDetector()
        self.schema_manager = SchemaVersionManager(self.repository)
        self.validator = SchemaValidator()
        self.scorer = QualityScorer(self.repository)
        self.drift_detector = DriftDetector(self.repository)
        self.lineage_tracker = LineageTracker(self.repository)
        self.version_manager = VersionManager(self.repository)

    def execute_quality_run(
        self,
        organization_id,
        dataset_name: str,
        rows: Iterable[dict],
        schema_overrides: dict | None = None,
        validation_rules_config: list[dict] | None = None,
        baseline_rows: Iterable[dict] | None = None,
        import_version: int = 1,
        transformation_version: int = 1,
        validation_version: int = 1,
    ) -> dict:
        rows = list(rows)
        profile = self.profiler.profile(rows)
        profile["organization_id"] = str(organization_id)
        profile["dataset_name"] = dataset_name
        schema = self.schema_detector.detect(rows, schema_overrides)

        normalized_org_id = uuid.UUID(str(organization_id)) if not isinstance(organization_id, uuid.UUID) else organization_id
        schema_def = self.schema_manager.create_definition(normalized_org_id, dataset_name, schema, schema_overrides)
        self.schema_manager.create_version(organization_id, schema_def.id, schema, "initial schema detection")

        validation_results = []
        duplicate_report = self._duplicate_analysis(rows)
        outlier_report = self._outlier_analysis(rows)

        if validation_rules_config:
            engine = ValidationRuleEngine.from_config(validation_rules_config)
            validation_results = engine.apply(rows)

        drift_report = None
        if baseline_rows is not None:
            drift_report = self.drift_detector.detect(organization_id, dataset_name, baseline_rows, rows)

        quality_score = self.scorer.score(profile, validation_results, duplicate_report, drift_report)

        lineage = {
            "source": "uploaded",
            "upload_time": datetime.utcnow().isoformat(),
            "dataset_name": dataset_name,
            "validation_rules": validation_rules_config or [],
            "schema_version": schema_def.id,
            "quality_score": quality_score.overall_score,
        }
        self.lineage_tracker.capture(organization_id, dataset_name, lineage)
        self.version_manager.create_version(
            organization_id,
            dataset_name,
            import_version,
            1,
            transformation_version,
            validation_version,
        )

        result = {
            "profile": profile,
            "schema": schema,
            "duplicates": duplicate_report,
            "outliers": outlier_report,
            "validation_results": validation_results,
            "drift": drift_report,
            "quality_score": {
                "overall": quality_score.overall_score,
                "grade": quality_score.grade,
                "categories": quality_score.category_scores,
            },
            "lineage": lineage,
        }

        return result

    def _duplicate_analysis(self, rows: list[dict]) -> dict:
        df = pd.DataFrame(rows)
        total_rows = len(df)
        if total_rows == 0:
            return {"duplicate_percentage": 0.0, "exact_matches": 0, "report": []}

        exact_matches = df.duplicated().sum()
        report = {
            "dataset_name": "",
            "duplicate_percentage": float((exact_matches / total_rows) * 100),
            "exact_matches": int(exact_matches),
        }
        return report

    def _outlier_analysis(self, rows: list[dict]) -> dict:
        df = pd.DataFrame(rows)
        outliers = {}
        for col in df.select_dtypes(include="number").columns:
            series = df[col].dropna()
            if series.empty:
                continue
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers[col] = {
                "count": int(((series < lower) | (series > upper)).sum()),
                "lower_bound": float(lower),
                "upper_bound": float(upper),
            }
        return outliers
