"""Feature selection service for CLV modeling."""
from __future__ import annotations

from typing import Any


class CLVFeatureSelectionService:
    def select_features(self, customers: list[dict[str, Any]], strategy: str = "importance") -> list[str]:
        base_features = [
            "total_spend",
            "average_order_value",
            "purchase_frequency",
            "total_orders",
            "lifetime_duration",
            "refund_amount",
            "discount_usage",
            "gross_margin",
            "website_sessions",
            "email_engagement",
            "product_views",
            "category_diversity",
            "purchase_interval",
            "customer_segment",
            "health_score",
            "loyalty_score",
            "satisfaction_score",
            "churn_probability",
            "rfm_score",
            "region",
            "customer_type",
            "industry",
            "acquisition_channel",
        ]
        if strategy == "importance":
            return base_features[:8]
        return base_features
