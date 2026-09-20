"""Dataset preparation service for churn modeling."""
from __future__ import annotations

from typing import Any


class ChurnDatasetService:
    def prepare_dataset(self, customers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        dataset = []
        for customer in customers:
            dataset.append(
                {
                    "customer_id": customer.get("customer_id"),
                    "days_since_last_purchase": customer.get("days_since_last_purchase", 0),
                    "days_since_last_login": customer.get("days_since_last_login", 0),
                    "purchase_frequency": customer.get("purchase_frequency", 0),
                    "session_frequency": customer.get("session_frequency", 0),
                    "support_ticket_count": customer.get("support_ticket_count", 0),
                    "product_returns": customer.get("product_returns", 0),
                    "total_revenue": customer.get("total_revenue", 0),
                    "average_order_value": customer.get("average_order_value", 0),
                    "lifetime_value": customer.get("lifetime_value", 0),
                    "subscription_status": customer.get("subscription_status", "active"),
                    "outstanding_payments": customer.get("outstanding_payments", 0),
                    "email_engagement": customer.get("email_engagement", 0),
                    "campaign_responses": customer.get("campaign_responses", 0),
                    "website_visits": customer.get("website_visits", 0),
                    "product_views": customer.get("product_views", 0),
                    "cart_abandonment": customer.get("cart_abandonment", 0),
                    "health_score": customer.get("health_score", 0),
                    "loyalty_score": customer.get("loyalty_score", 0),
                    "engagement_score": customer.get("engagement_score", 0),
                    "satisfaction_score": customer.get("satisfaction_score", 0),
                    "rfm_score": customer.get("rfm_score", 0),
                    "customer_segment": customer.get("customer_segment", "unknown"),
                    "churn_label": customer.get("churn_label", 0),
                }
            )
        return dataset
