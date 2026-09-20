import pytest

from clv_prediction.datasets.service import CLVDatasetService
from clv_prediction.preprocessing.service import CLVPreprocessingService
from clv_prediction.feature_selection.service import CLVFeatureSelectionService
from clv_prediction.training.service import CLVTrainingService
from clv_prediction.evaluation.service import CLVEvaluationService
from clv_prediction.inference.service import CLVInferenceService
from clv_prediction.customer_tiers.service import CustomerTierService
from clv_prediction.forecasting.service import CLVForecastingService
from clv_prediction.explainability.service import CLVExplainabilityService
from clv_prediction.monitoring.service import CLVMonitoringService
from clv_prediction.retraining.service import CLVRetrainingService
from clv_prediction.services.dashboard_service import CLVDashboardService


@pytest.fixture
def sample_customers() -> list[dict]:
    return [
        {"customer_id": "c1", "total_spend": 1500, "average_order_value": 300, "purchase_frequency": 5, "total_orders": 5, "lifetime_duration": 24, "refund_amount": 50, "discount_usage": 0.1, "gross_margin": 0.6, "website_sessions": 40, "email_engagement": 0.8, "product_views": 120, "category_diversity": 4, "purchase_interval": 5, "customer_segment": "champion", "health_score": 90, "loyalty_score": 88, "satisfaction_score": 92, "churn_probability": 0.1, "rfm_score": 5, "region": "north", "customer_type": "enterprise", "industry": "retail", "acquisition_channel": "organic", "target_clv": 6000},
        {"customer_id": "c2", "total_spend": 200, "average_order_value": 40, "purchase_frequency": 1, "total_orders": 1, "lifetime_duration": 3, "refund_amount": 20, "discount_usage": 0.5, "gross_margin": 0.2, "website_sessions": 8, "email_engagement": 0.1, "product_views": 15, "category_diversity": 1, "purchase_interval": 90, "customer_segment": "at_risk", "health_score": 20, "loyalty_score": 10, "satisfaction_score": 15, "churn_probability": 0.8, "rfm_score": 1, "region": "south", "customer_type": "small", "industry": "manufacturing", "acquisition_channel": "paid", "target_clv": 300},
    ]


def test_dataset_preparation(sample_customers: list[dict]) -> None:
    service = CLVDatasetService()
    dataset = service.prepare_dataset(sample_customers)
    assert len(dataset) == 2
    assert dataset[0]["customer_id"] == "c1"


def test_feature_selection(sample_customers: list[dict]) -> None:
    service = CLVFeatureSelectionService()
    selected = service.select_features(sample_customers, strategy="importance")
    assert len(selected) >= 3


def test_regression_training_and_evaluation(sample_customers: list[dict]) -> None:
    training = CLVTrainingService()
    evaluation = CLVEvaluationService()
    model = training.train(sample_customers)
    metrics = evaluation.evaluate(sample_customers, model)
    assert model["algorithm"] == "random_forest_regressor"
    assert metrics["r2"] >= 0.0


def test_prediction_pipeline_and_tiering(sample_customers: list[dict]) -> None:
    inference = CLVInferenceService()
    tiers = CustomerTierService()
    prediction = inference.predict(sample_customers[0], model={"version": "v1"})
    tier = tiers.assign_tier(prediction)
    assert prediction["predicted_clv"] > 0
    assert tier in {"Platinum", "Gold", "Silver", "Bronze", "Low Value"}


def test_forecasting_explainability_monitoring_and_retraining(sample_customers: list[dict]) -> None:
    forecasting = CLVForecastingService()
    explainability = CLVExplainabilityService()
    monitoring = CLVMonitoringService()
    retraining = CLVRetrainingService()
    dashboard = CLVDashboardService()

    forecast = forecasting.forecast(sample_customers, horizon="6m")
    explanation = explainability.explain(sample_customers[0], {"predicted_clv": 5000})
    monitoring.record_metrics({"average_predicted_clv": 4500})
    job = retraining.schedule_retraining({"trigger": "performance"})
    top_customers = dashboard.get_top_customers(sample_customers)

    assert forecast["total_forecast"] > 0
    assert "value" in explanation.lower()
    assert monitoring.get_metrics()[-1]["average_predicted_clv"] == 4500
    assert job["status"] == "scheduled"
    assert top_customers[0]["customer_id"] == "c1"
