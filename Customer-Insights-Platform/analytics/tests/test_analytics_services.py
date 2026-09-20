import pytest

from analytics.services.analytics_service import AnalyticsService


@pytest.fixture
def service() -> AnalyticsService:
    return AnalyticsService()


def test_calculate_metric_basic(service: AnalyticsService) -> None:
    records = [
        {"customer_id": "c1", "active": True, "is_new": True, "amount": 10.0},
        {"customer_id": "c2", "active": True, "is_new": False, "amount": 20.0},
        {"customer_id": "c3", "active": False, "is_new": False, "amount": 5.0},
    ]

    assert service.calculate_metric("total_customers", records) == 3
    assert service.calculate_metric("active_customers", records) == 2
    assert service.calculate_metric("new_customers", records) == 1
    assert service.calculate_metric("revenue", records) == 35.0


def test_generate_cohort_and_rfm(service: AnalyticsService) -> None:
    records = [
        {"customer_id": "c1", "signup_month": "2024-01", "recency": 30, "frequency": 5, "monetary": 150.0},
        {"customer_id": "c2", "signup_month": "2024-01", "recency": 60, "frequency": 2, "monetary": 80.0},
        {"customer_id": "c3", "signup_month": "2024-02", "recency": 10, "frequency": 7, "monetary": 200.0},
    ]

    cohorts = service.generate_cohort(records)
    assert len(cohorts) == 2
    assert any(cohort["group"] == "2024-01" for cohort in cohorts)

    rfm = service.calculate_rfm(records)
    assert any(item["segment"] == "champion" for item in rfm)


def test_funnel_retention_and_growth(service: AnalyticsService) -> None:
    records = [
        {"lead": True, "qualified": True, "won": True, "returned": True},
        {"lead": True, "qualified": False, "won": False, "returned": False},
    ]

    funnel = service.generate_funnel(records, ["lead", "qualified", "won"])
    assert funnel["counts"] == [2, 1, 1]

    retention = service.calculate_retention(records)
    assert retention["returning_customers"] == 1

    growth = service.calculate_growth([{"value": 100}, {"value": 120}])
    assert growth["growth_rate"] == 0.2
