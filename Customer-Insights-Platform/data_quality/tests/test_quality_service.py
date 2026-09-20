import pytest

from data_quality.services.quality_service import DataQualityService
from data_quality.rules.email_rule import EmailFormatRule
from data_quality.rules.unique_rule import UniqueFieldRule
from data_quality.rules.registry import rule_registry


@pytest.fixture(autouse=True)
def register_rules():
    rule_registry.register(EmailFormatRule)
    rule_registry.register(UniqueFieldRule)


def test_profile_and_schema_detection():
    rows = [
        {"customer_id": "1", "email": "test@example.com", "revenue": 100.0, "country": "US"},
        {"customer_id": "2", "email": "hello@example.com", "revenue": 150.0, "country": "CA"},
    ]

    service = DataQualityService()
    result = service.execute_quality_run(
        organization_id="00000000-0000-0000-0000-000000000000",
        dataset_name="customers",
        rows=rows,
        validation_rules_config=[
            {"name": "EmailFormatRule", "params": {}},
        ],
    )

    assert result["profile"]["total_rows"] == 2
    assert "schema" in result
    assert result["quality_score"]["overall"] >= 0


def test_validation_rule_engine():
    rows = [{"email": "invalid"}, {"email": "valid@example.com"}]
    engine = DataQualityService().validator
    schema_spec = {"columns": {"email": {"detected_type": "email"}}}

    with pytest.raises(Exception):
        engine.validate(rows, schema_spec)
