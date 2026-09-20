import pytest

from customer_segmentation.rfm.service import RFMService
from customer_segmentation.preprocessing.service import DataPreparationService
from customer_segmentation.clustering.service import KMeansSegmentationService
from customer_segmentation.training.service import SegmentationTrainingService
from customer_segmentation.profiling.service import SegmentProfilingService
from customer_segmentation.assignment.service import AssignmentService
from customer_segmentation.monitoring.service import SegmentMonitoringService
from customer_segmentation.drift.service import DriftDetectionService
from customer_segmentation.naming.service import SegmentNamingService
from customer_segmentation.summary.service import SummaryService


@pytest.fixture
def sample_customers() -> list[dict]:
    return [
        {"customer_id": "c1", "recency": 5, "frequency": 10, "monetary": 200, "avg_order_value": 20, "orders_per_month": 2.0, "customer_lifetime": 24, "purchase_interval": 5, "total_revenue": 2000, "product_diversity": 4, "category_diversity": 3, "session_count": 15, "website_activity": 10, "email_engagement": 8, "campaign_engagement": 5, "support_interactions": 1, "days_since_last_activity": 5, "health_score": 92, "loyalty_score": 88, "engagement_score": 90},
        {"customer_id": "c2", "recency": 45, "frequency": 2, "monetary": 40, "avg_order_value": 20, "orders_per_month": 0.5, "customer_lifetime": 6, "purchase_interval": 60, "total_revenue": 300, "product_diversity": 1, "category_diversity": 1, "session_count": 3, "website_activity": 2, "email_engagement": 1, "campaign_engagement": 0, "support_interactions": 3, "days_since_last_activity": 40, "health_score": 40, "loyalty_score": 20, "engagement_score": 25},
        {"customer_id": "c3", "recency": 15, "frequency": 7, "monetary": 140, "avg_order_value": 20, "orders_per_month": 1.2, "customer_lifetime": 14, "purchase_interval": 10, "total_revenue": 1200, "product_diversity": 3, "category_diversity": 2, "session_count": 10, "website_activity": 8, "email_engagement": 6, "campaign_engagement": 4, "support_interactions": 2, "days_since_last_activity": 12, "health_score": 78, "loyalty_score": 72, "engagement_score": 75},
    ]


def test_rfm_scoring_and_classification(sample_customers: list[dict]) -> None:
    service = RFMService()
    scored = service.score(sample_customers)
    assert any(item["rfm_category"] for item in scored)


def test_data_preparation_uses_feature_store_features(sample_customers: list[dict]) -> None:
    service = DataPreparationService()
    prepared = service.prepare(sample_customers)
    assert prepared[0]["recency"] == 5
    assert prepared[0]["monetary"] == 200


def test_kmeans_training_and_cluster_selection(sample_customers: list[dict]) -> None:
    training = SegmentationTrainingService()
    model = training.train(sample_customers)
    assert model["cluster_count"] >= 1

    clustering = KMeansSegmentationService()
    result = clustering.predict(sample_customers, model)
    assert len(result) == len(sample_customers)


def test_segment_profiling_assignment_and_monitoring(sample_customers: list[dict]) -> None:
    profiling = SegmentProfilingService()
    assignment = AssignmentService()
    monitoring = SegmentMonitoringService()
    naming = SegmentNamingService()

    profile = profiling.build_profile(sample_customers)
    assignment_result = assignment.assign(sample_customers, "segment-1")
    monitoring.record_growth("segment-1", 5)

    assert profile["customer_count"] == 3
    assert assignment_result[0]["segment_id"] == "segment-1"
    assert monitoring.get_history("segment-1")[-1]["growth"] == 5
    assert naming.generate_name("high", "loyal") == "High Growth Customers"


def test_drift_detection_and_summary_generation(sample_customers: list[dict]) -> None:
    drift = DriftDetectionService()
    summary = SummaryService()

    drift_result = drift.detect(sample_customers, sample_customers)
    assert drift_result["drift_detected"] is False

    summary_text = summary.generate(sample_customers, "High Value")
    assert "revenue" in summary_text.lower()
