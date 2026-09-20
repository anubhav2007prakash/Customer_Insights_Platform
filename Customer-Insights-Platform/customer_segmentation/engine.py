"""Main customer segmentation engine orchestrator."""
from __future__ import annotations

from typing import Any

from customer_segmentation.assignment.service import AssignmentService
from customer_segmentation.clustering.service import KMeansSegmentationService
from customer_segmentation.drift.service import DriftDetectionService
from customer_segmentation.monitoring.service import MonitoringService
from customer_segmentation.naming.service import SegmentNamingService
from customer_segmentation.preprocessing import service as preprocessing_service
from customer_segmentation.profiling.service import SegmentProfilingService
from customer_segmentation.rfm.service import RFMService
from customer_segmentation.summary.service import SegmentationSummaryService
from customer_segmentation.training.service import SegmentationTrainingService


class CustomerSegmentationEngine:
    def __init__(self) -> None:
        self.preprocessing = preprocessing_service.DataPreparationService()
        self.rfm = RFMService()
        self.training = SegmentationTrainingService()
        self.clustering = KMeansSegmentationService()
        self.profiling = SegmentProfilingService()
        self.assignment = AssignmentService()
        self.monitoring = MonitoringService()
        self.drift = DriftDetectionService()
        self.naming = SegmentNamingService()
        self.summary = SegmentationSummaryService()

    def segment(self, customers: list[dict[str, Any]]) -> dict[str, Any]:
        prepared = self.preprocessing.prepare(customers)
        scored = self.rfm.score(prepared)
        model = self.training.train(prepared)
        cluster_assignments = self.clustering.predict(prepared, model)
        assignments = self.assignment.assign(prepared, cluster_assignments)
        profile = self.profiling.build_profile(prepared)
        monitoring = self.monitoring.monitor(assignments)
        name = self.naming.name(profile)
        summary = self.summary.summarize(profile, name, monitoring)
        drift = self.drift.detect(prepared, prepared)
        return {
            "model": model,
            "rfm_scores": scored,
            "assignments": assignments,
            "profile": profile,
            "monitoring": monitoring,
            "drift": drift,
            "segment_name": name,
            "summary": summary,
        }
