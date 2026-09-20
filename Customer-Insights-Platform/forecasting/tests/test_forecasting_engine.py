import pytest

from forecasting.datasets.service import ForecastDatasetService
from forecasting.preprocessing.service import ForecastPreprocessingService
from forecasting.feature_engineering.service import FeatureEngineeringService
from forecasting.training.service import ForecastTrainingService
from forecasting.inference.service import ForecastInferenceService
from forecasting.scenarios.service import ScenarioSimulationService
from forecasting.monitoring.service import MonitoringService
from forecasting.retraining.service import RetrainingService
from forecasting.services.dashboard_service import ForecastDashboardService


@pytest.fixture
def sample_series():
    return [
        {"date": "2024-01-01", "value": 100.0, "product": "widget", "region": "north"},
        {"date": "2024-02-01", "value": 120.0, "product": "widget", "region": "north"},
        {"date": "2024-03-01", "value": 140.0, "product": "widget", "region": "north"},
        {"date": "2024-04-01", "value": 160.0, "product": "widget", "region": "north"},
    ]


def test_dataset_preparation(sample_series):
    service = ForecastDatasetService()
    dataset = service.prepare_dataset(sample_series)
    assert dataset[0]["series_id"] == "widget:north"
    assert dataset[0]["value"] == 100.0


def test_feature_engineering(sample_series):
    service = FeatureEngineeringService()
    features = service.generate_features(sample_series, horizon=2, frequency="monthly")
    assert features[0]["month"] in {1, 2, 3, 4}
    assert len(features) >= 2


def test_model_training(sample_series):
    training = ForecastTrainingService()
    model = training.train(sample_series, target="value", model_type="random_forest")
    assert model["model_type"] == "random_forest"
    assert model["status"] == "trained"


def test_forecast_generation(sample_series):
    inference = ForecastInferenceService()
    forecast = inference.generate_forecast(sample_series, horizon=2, frequency="monthly")
    assert len(forecast["forecast"]) == 2
    assert forecast["forecast"][0]["value"] >= 0


def test_scenario_simulation(sample_series):
    service = ScenarioSimulationService()
    scenarios = service.generate_scenarios(sample_series, horizon=2)
    assert {scenario["name"] for scenario in scenarios} >= {"best_case", "expected_case", "worst_case"}


def test_monitoring(sample_series):
    service = MonitoringService()
    service.record_metrics({"accuracy": 0.91, "bias": 0.02})
    metrics = service.get_metrics()
    assert metrics[-1]["accuracy"] == 0.91


def test_retraining(sample_series):
    service = RetrainingService()
    job = service.trigger_retraining(sample_series, strategy="performance")
    assert job["status"] == "scheduled"
    assert job["strategy"] == "performance"


def test_dashboard_services(sample_series):
    dashboard = ForecastDashboardService()
    sales = dashboard.sales_forecast(sample_series, horizon=2)
    demand = dashboard.demand_forecast(sample_series, horizon=2)
    accuracy = dashboard.forecast_accuracy(sample_series)
    assert sales["forecast"][0]["value"] >= 0
    assert demand["forecast"][0]["value"] >= 0
    assert accuracy["accuracy"] >= 0
