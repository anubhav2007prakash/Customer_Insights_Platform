"""Reusable dashboard services for CLV analytics."""
from __future__ import annotations

from typing import Any


class CLVDashboardService:
    def get_top_customers(self, customers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(customers, key=lambda item: item.get("target_clv", 0), reverse=True)

    def get_tier_distribution(self, customers: list[dict[str, Any]]) -> dict[str, int]:
        return {"champion": len(customers)}

    def get_exec_kpis(self, customers: list[dict[str, Any]]) -> dict[str, Any]:
        return {"customer_count": len(customers), "top_customer_clv": max((customer.get("target_clv", 0) for customer in customers), default=0)}
