"""Reusable dashboard-facing services for churn analytics."""
from __future__ import annotations

from typing import Any


class ChurnDashboardService:
    def get_high_risk_customers(self, customers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [customer for customer in customers if customer.get("health_score", 0) < 40]

    def get_churn_distribution(self, customers: list[dict[str, Any]]) -> dict[str, int]:
        return {"churned": sum(1 for customer in customers if customer.get("churn_label", 0) == 1), "retained": sum(1 for customer in customers if customer.get("churn_label", 0) == 0)}

    def get_exec_kpis(self, customers: list[dict[str, Any]]) -> dict[str, Any]:
        return {"customer_count": len(customers), "high_risk_count": len(self.get_high_risk_customers(customers))}
