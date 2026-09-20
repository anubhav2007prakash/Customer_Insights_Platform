"""Central registry for analytics metrics and KPIs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricDefinition:
    metric_id: str
    name: str
    description: str
    category: str
    formula: str
    unit: str
    aggregation_method: str
    refresh_strategy: str = "on_demand"
    owner: str = "analytics"
    status: str = "active"
    version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)


class MetricRegistry:
    def __init__(self):
        self._metrics: dict[str, MetricDefinition] = {}
        self._register_default_metrics()

    def _register_default_metrics(self) -> None:
        for definition in [
            MetricDefinition("total_customers", "Total Customers", "Customer KPI", "customer", "count(distinct customer_id)", "count", "count", "on_demand"),
            MetricDefinition("active_customers", "Active Customers", "Customer KPI", "customer", "count(distinct customer_id where active=true)", "count", "count", "on_demand"),
            MetricDefinition("new_customers", "New Customers", "Customer KPI", "customer", "count(distinct customer_id where created_at in range)", "count", "count", "on_demand"),
            MetricDefinition("revenue", "Revenue", "Sales KPI", "sales", "sum(amount)", "currency", "sum", "on_demand"),
            MetricDefinition("orders", "Orders", "Sales KPI", "sales", "count(distinct order_id)", "count", "count", "on_demand"),
            MetricDefinition("leads", "Leads", "Marketing KPI", "marketing", "count(distinct lead_id)", "count", "count", "on_demand"),
            MetricDefinition("ctr", "CTR", "Marketing KPI", "marketing", "clicks/impressions", "percent", "ratio", "on_demand"),
        ]:
            self.register(definition)

    def register(self, definition: MetricDefinition) -> MetricDefinition:
        self._metrics[definition.metric_id] = definition
        return definition

    def get(self, metric_id: str) -> MetricDefinition | None:
        return self._metrics.get(metric_id)

    def list(self) -> list[MetricDefinition]:
        return list(self._metrics.values())
