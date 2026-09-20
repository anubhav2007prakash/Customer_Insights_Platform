"""High-level analytics service for KPI and cohort calculation."""
from __future__ import annotations

from typing import Any

from analytics.registry.metric_registry import MetricRegistry
from analytics.cohorts.service import CohortService
from analytics.funnels.service import FunnelService
from analytics.retention.service import RetentionService
from analytics.rfm.service import RFMService
from analytics.growth.service import GrowthService
from analytics.executive.service import ExecutiveScorecardService
from analytics.cache.service import CacheService


class AnalyticsService:
    def __init__(self, registry: MetricRegistry | None = None):
        self.registry = registry or MetricRegistry()
        self.cohort_service = CohortService()
        self.funnel_service = FunnelService()
        self.retention_service = RetentionService()
        self.rfm_service = RFMService()
        self.growth_service = GrowthService()
        self.executive_service = ExecutiveScorecardService()
        self.cache_service = CacheService()

    def calculate_metric(self, metric_id: str, records: list[dict[str, Any]], **filters: Any) -> Any:
        cached = self.cache_service.get(metric_id, filters)
        if cached is not None:
            return cached

        metric = self.registry.get(metric_id)
        if metric is None:
            raise ValueError(f"Unknown metric: {metric_id}")

        result = self._basic_metric(metric_id, records)
        self.cache_service.set(metric_id, filters, result)
        return result

    def calculate_kpi(self, metric_id: str, records: list[dict[str, Any]], **filters: Any) -> Any:
        return self.calculate_metric(metric_id, records, **filters)

    def calculate_rfm(self, records: list[dict[str, Any]], thresholds: dict[str, int] | None = None) -> list[dict[str, Any]]:
        return self.rfm_service.calculate(records, thresholds or {})

    def generate_cohort(self, records: list[dict[str, Any]], group_by: str = "signup_month") -> list[dict[str, Any]]:
        return self.cohort_service.generate(records, group_by)

    def generate_funnel(self, records: list[dict[str, Any]], stages: list[str]) -> dict[str, Any]:
        return self.funnel_service.generate(records, stages)

    def calculate_retention(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        return self.retention_service.calculate(records)

    def calculate_growth(self, values: list[dict[str, Any]]) -> dict[str, Any]:
        return self.growth_service.calculate(values)

    def generate_executive_scorecard(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        return self.executive_service.generate(records)

    def _basic_metric(self, metric_id: str, records: list[dict[str, Any]]) -> Any:
        if metric_id == "total_customers":
            return len({record.get("customer_id") for record in records if record.get("customer_id")})
        if metric_id == "active_customers":
            return sum(1 for record in records if record.get("active"))
        if metric_id == "new_customers":
            return sum(1 for record in records if record.get("is_new"))
        if metric_id == "revenue":
            return sum(float(record.get("amount", 0)) for record in records)
        if metric_id == "orders":
            return len(records)
        if metric_id == "leads":
            return sum(1 for record in records if record.get("lead"))
        if metric_id == "ctr":
            clicks = sum(1 for record in records if record.get("clicked"))
            impressions = max(1, len(records))
            return round(clicks / impressions, 4)
        raise ValueError(f"No calculator registered for {metric_id}")
