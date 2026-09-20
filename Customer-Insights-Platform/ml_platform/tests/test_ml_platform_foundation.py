import pytest

from ml_platform.datasets.manager import DatasetManager
from ml_platform.preprocessing.pipeline import PreprocessingPipeline
from ml_platform.feature_engineering.engine import FeatureEngineeringService
from ml_platform.feature_store.store import FeatureStore
from ml_platform.training.trainer import ModelTrainer
from ml_platform.evaluation.metrics import EvaluationService
from ml_platform.registry.manager import ModelRegistry
from ml_platform.versioning.manager import ModelVersionManager
from ml_platform.inference.service import InferenceService
from ml_platform.experiments.manager import ExperimentTracker
from ml_platform.monitoring.service import MonitoringService


@pytest.fixture
def dataset_manager() -> DatasetManager:
    return DatasetManager()


def test_dataset_registration_and_split(dataset_manager: DatasetManager) -> None:
    dataset = dataset_manager.register_dataset(
        name="customer_churn",
        version="v1",
        metadata={"source": "crm"},
        rows=[{"customer_id": 1, "age": 30, "income": 1000, "label": 1}, {"customer_id": 2, "age": 25, "income": 2000, "label": 0}],
    )

    assert dataset.name == "customer_churn"
    train, test = dataset_manager.train_test_split(dataset, test_size=0.5)
    assert len(train) == 1
    assert len(test) == 1


def test_preprocessing_pipeline_handles_missing_and_scaling() -> None:
    pipeline = PreprocessingPipeline()
    rows = [{"age": 30, "income": 1000.0, "label": 1}, {"age": None, "income": 2000.0, "label": 0}]

    transformed = pipeline.fit_transform(rows)
    assert len(transformed) == 2
    assert transformed[0]["age"] >= 0


def test_feature_engineering_adds_behavioral_features() -> None:
    service = FeatureEngineeringService()
    rows = [{"customer_id": 1, "purchase_count": 5, "avg_order_value": 20.0, "days_since_last_purchase": 10}, {"customer_id": 2, "purchase_count": 1, "avg_order_value": 5.0, "days_since_last_purchase": 100}]

    features = service.build_features(rows)
    assert any("purchase_frequency" in item for item in features)
    assert any("customer_age_band" in item for item in features)


def test_feature_store_registers_and_retrieves_features() -> None:
    store = FeatureStore()
    feature = store.register_feature(name="purchase_frequency", description="Count of purchases", data_type="float", source="orders", version="v1", owner="ml")

    assert store.get_feature("purchase_frequency") == feature


def test_training_and_evaluation_pipeline() -> None:
    trainer = ModelTrainer()
    rows = [{"age": 20, "income": 1000, "label": 0}, {"age": 30, "income": 3000, "label": 1}, {"age": 40, "income": 5000, "label": 1}]

    model = trainer.train(rows, task_type="classification")
    assert model is not None

    evaluator = EvaluationService()
    metrics = evaluator.evaluate(model, rows, task_type="classification")
    assert metrics["accuracy"] >= 0


def test_registry_and_versioning_flow() -> None:
    registry = ModelRegistry()
    versioning = ModelVersionManager()
    model = {"name": "churn_model", "algorithm": "logistic_regression", "status": "draft"}
    registered = registry.register(model)
    versioned = versioning.create_version(registered)

    assert versioned["version"] == "v1"
    assert registry.get(registered["model_id"]).get("status") == "draft"


def test_inference_and_experiment_tracking() -> None:
    inference = InferenceService()
    prediction = inference.predict_single({"age": 35, "income": 4000}, model={"algorithm": "logistic_regression"})
    assert prediction in {0, 1}

    tracker = ExperimentTracker()
    experiment = tracker.create_experiment(name="baseline", params={"max_depth": 3})
    assert experiment["name"] == "baseline"


def test_monitoring_records_metrics() -> None:
    monitoring = MonitoringService()
    record = monitoring.record_prediction(latency_ms=12.5, error=False)
    assert record["prediction_count"] == 1
