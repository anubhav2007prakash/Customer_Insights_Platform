import pytest

from churn_prediction.datasets.service import ChurnDatasetService
from churn_prediction.preprocessing.service import ChurnPreprocessingService
from churn_prediction.feature_selection.service import ChurnFeatureSelectionService
from churn_prediction.training.service import ChurnTrainingService
from churn_prediction.evaluation.service import ChurnEvaluationService
from churn_prediction.inference.service import ChurnInferenceService
from churn_prediction.explainability.service import ChurnExplainabilityService
from churn_prediction.recommendations.service import ChurnRecommendationService
from churn_prediction.monitoring.service import ChurnMonitoringService
from churn_prediction.retraining.service import ChurnRetrainingService
from churn_prediction.services.dashboard_service import ChurnDashboardService


@pytest.fixture
def sample_customers() -> list[dict]:
    return [
        {"customer_id": "c1", "days_since_last_purchase": 12, "days_since_last_login": 10, "purchase_frequency": 5, "session_frequency": 3, "support_ticket_count": 1, "product_returns": 0, "total_revenue": 1200, "average_order_value": 240, "lifetime_value": 5000, "subscription_status": "active", "outstanding_payments": 0, "email_engagement": 0.8, "campaign_responses": 2, "website_visits": 14, "product_views": 20, "cart_abandonment": 1, "health_score": 90, "loyalty_score": 88, "engagement_score": 85, "satisfaction_score": 92, "rfm_score": 4, "customer_segment": "champion", "churn_label": 0},
        {"customer_id": "c2", "days_since_last_purchase": 90, "days_since_last_login": 80, "purchase_frequency": 1, "session_frequency": 1, "support_ticket_count": 4, "product_returns": 2, "total_revenue": 200, "average_order_value": 50, "lifetime_value": 600, "subscription_status": "inactive", "outstanding_payments": 120, "email_engagement": 0.1, "campaign_responses": 0, "website_visits": 2, "product_views": 3, "cart_abandonment": 4, "health_score": 20, "loyalty_score": 10, "engagement_score": 15, "satisfaction_score": 12, "rfm_score": 1, "customer_segment": "at_risk", "churn_label": 1},
    ]


def test_dataset_preparation(sample_customers: list[dict]) -> None:
    service = ChurnDatasetService()
    dataset = service.prepare_dataset(sample_customers)
    assert len(dataset) == 2
    assert dataset[0]["customer_id"] == "c1"


def test_label_generation(sample_customers: list[dict]) -> None:
    service = ChurnPreprocessingService()
    labels = service.generate_labels(sample_customers, rules={"inactivity_days": 60})
    assert labels[0] == 0
    assert labels[1] == 1


def test_feature_selection(sample_customers: list[dict]) -> None:
    service = ChurnFeatureSelectionService()
    selected = service.select_features(sample_customers, strategy="importance")
    assert len(selected) >= 3


def test_model_training_and_evaluation(sample_customers: list[dict]) -> None:
    training = ChurnTrainingService()
    evaluation = ChurnEvaluationService()
    model = training.train(sample_customers)
    metrics = evaluation.evaluate(sample_customers, model)
    assert model["algorithm"] == "random_forest"
    assert metrics["accuracy"] >= 0.0


def test_prediction_pipeline_and_explainability(sample_customers: list[dict]) -> None:
    inference = ChurnInferenceService()
    explain = ChurnExplainabilityService()
    prediction = inference.predict(sample_customers[1], model={"version": "v1"})
    explanation = explain.explain(sample_customers[1], prediction)
    assert prediction["risk_level"] in {"Very Low", "Low", "Medium", "High", "Critical"}
    assert "churn" in explanation.lower()


def test_recommendations_monitoring_and_retraining(sample_customers: list[dict]) -> None:
    recommendations = ChurnRecommendationService()
    monitoring = ChurnMonitoringService()
    retraining = ChurnRetrainingService()
    dashboard = ChurnDashboardService()

    recs = recommendations.generate(sample_customers[1])
    monitoring.record_metrics({"accuracy": 0.88})
    job = retraining.schedule_retraining({"trigger": "drift"})
    high_risk = dashboard.get_high_risk_customers(sample_customers)

    assert recs
    assert monitoring.get_metrics()[-1]["accuracy"] == 0.88
    assert job["status"] == "scheduled"
    assert high_risk[0]["customer_id"] == "c2"
