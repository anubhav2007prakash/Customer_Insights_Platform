"""Calculate data quality scores and grade categories."""
from __future__ import annotations

from datetime import datetime
from typing import Dict

from data_quality.repositories.repository import DataQualityRepository
from data_quality.repositories.models import DataQualityScore


class QualityScorer:
    def __init__(self, repository: DataQualityRepository | None = None):
        self.repository = repository or DataQualityRepository()

    def score(self, profile: dict, validation_results: list[dict], duplicate_report: dict | None = None, drift_report: dict | None = None) -> DataQualityScore:
        completeness = self._score_completeness(profile)
        validity = self._score_validity(validation_results)
        uniqueness = self._score_uniqueness(profile, duplicate_report)
        consistency = self._score_consistency(profile)
        accuracy = self._score_accuracy(validation_results)
        timeliness = self._score_timeliness(drift_report)

        category_scores = {
            "completeness": completeness,
            "validity": validity,
            "uniqueness": uniqueness,
            "consistency": consistency,
            "accuracy": accuracy,
            "timeliness": timeliness,
        }
        overall_score = sum(category_scores.values()) / len(category_scores)
        grade = self._grade(overall_score)

        score = DataQualityScore(
            organization_id=profile.get("organization_id"),
            dataset_name=profile.get("dataset_name"),
            overall_score=overall_score,
            category_scores=category_scores,
            grade=grade,
            generated_at=datetime.utcnow(),
        )
        return self.repository.add_quality_score(score)

    def _score_completeness(self, profile: dict) -> float:
        return 100.0 - float(max(profile.get("null_percentage", {}).values(), default=0.0))

    def _score_validity(self, validation_results: list[dict]) -> float:
        total = 0
        passed = 0
        for row in validation_results:
            for item in row["validations"]:
                total += 1
                if item["passed"]:
                    passed += 1
        return float((passed / total) * 100) if total else 100.0

    def _score_uniqueness(self, profile: dict, duplicate_report: dict | None) -> float:
        if not duplicate_report:
            return 100.0
        duplicate_rate = duplicate_report.get("duplicate_percentage", 0.0)
        return max(0.0, 100.0 - duplicate_rate)

    def _score_consistency(self, profile: dict) -> float:
        return 100.0 if profile.get("duplicate_percentage", 0.0) < 5.0 else 80.0

    def _score_accuracy(self, validation_results: list[dict]) -> float:
        return self._score_validity(validation_results)

    def _score_timeliness(self, drift_report: dict | None) -> float:
        if not drift_report:
            return 100.0
        return max(0.0, 100.0 - float(drift_report.get("drift_score", 0.0)))

    def _grade(self, score: float) -> str:
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"
