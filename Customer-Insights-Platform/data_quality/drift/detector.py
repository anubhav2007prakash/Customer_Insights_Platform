"""Detect data drift by comparing dataset statistics to historical baselines."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable
import pandas as pd

from data_quality.repositories.repository import DataQualityRepository
from data_quality.repositories.models import DriftReport


class DriftDetector:
    def __init__(self, repository: DataQualityRepository | None = None):
        self.repository = repository or DataQualityRepository()

    def detect(self, organization_id, dataset_name: str, baseline_rows: Iterable[dict], target_rows: Iterable[dict]) -> DriftReport:
        baseline_df = pd.DataFrame(baseline_rows)
        target_df = pd.DataFrame(target_rows)

        drift_metrics = self._compare(baseline_df, target_df)
        report = DriftReport(
            organization_id=organization_id,
            dataset_name=dataset_name,
            baseline_version=1,
            target_version=2,
            drift_metrics=drift_metrics,
            generated_at=datetime.utcnow(),
        )
        return self.repository.add_drift_report(report)

    def _compare(self, baseline_df: pd.DataFrame, target_df: pd.DataFrame) -> dict:
        metrics = {
            "baseline_row_count": int(baseline_df.shape[0]),
            "target_row_count": int(target_df.shape[0]),
            "missing_value_change": {},
            "distribution_change": {},
            "drift_score": 0.0,
        }

        for col in set(baseline_df.columns).union(set(target_df.columns)):
            baseline = baseline_df.get(col, pd.Series(dtype=object))
            target = target_df.get(col, pd.Series(dtype=object))

            baseline_null = float(baseline.isna().sum()) / max(len(baseline), 1)
            target_null = float(target.isna().sum()) / max(len(target), 1)

            metrics["missing_value_change"][col] = target_null - baseline_null
            metrics["distribution_change"][col] = float(abs(target.nunique(dropna=True) - baseline.nunique(dropna=True)))

        metrics["drift_score"] = float(sum(abs(v) for v in metrics["missing_value_change"].values()) + sum(metrics["distribution_change"].values()))
        return metrics
