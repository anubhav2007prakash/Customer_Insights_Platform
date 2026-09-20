"""Data preparation service for segmentation."""
from __future__ import annotations

from typing import Any


class DataPreparationService:
    def prepare(self, customers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        prepared = []
        for customer in customers:
            prepared.append(
                {
                    "customer_id": customer.get("customer_id"),
                    "recency": customer.get("recency", 0),
                    "frequency": customer.get("frequency", 0),
                    "monetary": customer.get("monetary", 0),
                    "avg_order_value": customer.get("avg_order_value", 0),
                    "orders_per_month": customer.get("orders_per_month", 0),
                    "customer_lifetime": customer.get("customer_lifetime", 0),
                    "purchase_interval": customer.get("purchase_interval", 0),
                    "total_revenue": customer.get("total_revenue", 0),
                    "product_diversity": customer.get("product_diversity", 0),
                    "category_diversity": customer.get("category_diversity", 0),
                    "session_count": customer.get("session_count", 0),
                    "website_activity": customer.get("website_activity", 0),
                    "email_engagement": customer.get("email_engagement", 0),
                    "campaign_engagement": customer.get("campaign_engagement", 0),
                    "support_interactions": customer.get("support_interactions", 0),
                    "days_since_last_activity": customer.get("days_since_last_activity", 0),
                }
            )
        return prepared
