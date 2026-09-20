import pytest

from feature_store.registry.service import FeatureRegistryService
from feature_store.catalog.service import FeatureCatalogService
from feature_store.engineering.service import FeatureEngineeringService
from feature_store.validation.service import FeatureValidationService
from feature_store.versioning.service import FeatureVersionService
from feature_store.lineage.service import FeatureLineageService
from feature_store.freshness.service import FeatureFreshnessService
from feature_store.serving.service import FeatureServingService
from feature_store.monitoring.service import FeatureMonitoringService
from feature_store.cache.service import FeatureCacheService


@pytest.fixture
def registry() -> FeatureRegistryService:
    return FeatureRegistryService()


def test_feature_registration_and_catalog_search(registry: FeatureRegistryService) -> None:
    feature = registry.register_feature(
        name="customer_age",
        description="Customer age in years",
        category="customer",
        owner="ml",
        source_dataset="customers",
        data_type="int",
        refresh_frequency="daily",
        tags=["customer", "demographic"],
    )

    catalog = FeatureCatalogService()
    results = catalog.search(category="customer", owner="ml")
    assert any(item["feature_id"] == feature["feature_id"] for item in results)


def test_feature_engineering_generates_customer_features() -> None:
    service = FeatureEngineeringService()
    rows = [{"customer_id": 1, "age": 35, "days_since_last_purchase": 10, "purchase_count": 5, "avg_order_value": 20.0, "total_spend": 100.0}]
    features = service.generate_features(rows, "customer")
    assert any(feature["name"] == "customer_age" for feature in features)
    assert any(feature["name"] == "days_since_last_purchase" for feature in features)


def test_validation_rejects_invalid_feature_definitions() -> None:
    service = FeatureValidationService()
    invalid = {"name": "bad_feature", "null_percentage": 0.95, "cardinality": 1, "data_type": "int"}
    result = service.validate(invalid)
    assert result["approved"] is False


def test_versioning_and_lineage_tracking() -> None:
    versioning = FeatureVersionService()
    lineage = FeatureLineageService()
    feature = {"feature_id": "f1", "name": "customer_age"}
    versioned = versioning.create_version(feature, "initial version")
    lineage_record = lineage.record(feature, ["customers"], ["etl_pipeline"])
    assert versioned["version"] == "v1"
    assert lineage_record["source_tables"] == ["customers"]


def test_freshness_serving_and_monitoring() -> None:
    freshness = FeatureFreshnessService()
    service = FeatureServingService()
    monitoring = FeatureMonitoringService()
    cache = FeatureCacheService()

    freshness.update_last_refresh("customer_age", stale=True)
    result = service.get_feature("customer_age", {"customer_id": 1})
    assert result["name"] == "customer_age"

    monitoring.record_usage("customer_age")
    cache.set("customer_age", {"value": 35})
    cached = cache.get("customer_age")
    assert cached["value"] == 35
