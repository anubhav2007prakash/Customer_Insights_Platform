"""Feature selection service for churn modeling."""
from __future__ import annotations

from typing import Any


class ChurnFeatureSelectionService:
    def select_features(self, customers: list[dict[str, Any]], strategy: str = "importance") -> list[str]:
        base_features = [
            "days_since_last_purchase",
            "days_since_last_login",
            "purchase_frequency",
            "session_frequency",
            "support_ticket_count",
            "product_returns",
            "total_revenue",
            "average_order_value",
            "lifetime_value",
            "subscription_status",
            "outstanding_payments",
            "email_engagement",
            "campaign_responses",
            "website_visits",
            "product_views",
            "cart_abandonment",
            "health_score",
            "loyalty_score",
            "engagement_score",
            "satisfaction_score",
            "rfm_score",
            "customer_segment",
        ]
        if strategy == "importance":
            return base_features[:8]
        return base_features
