"""Dataset preparation service for CLV modeling."""
from __future__ import annotations

from typing import Any


class CLVDatasetService:
    def prepare_dataset(self, customers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        dataset = []
        for customer in customers:
            dataset.append(
                {
                    "customer_id": customer.get("customer_id"),
                    "total_spend": customer.get("total_spend", 0),
                    "average_order_value": customer.get("average_order_value", 0),
                    "purchase_frequency": customer.get("purchase_frequency", 0),
                    "total_orders": customer.get("total_orders", 0),
                    "lifetime_duration": customer.get("lifetime_duration", 0),
                    "refund_amount": customer.get("refund_amount", 0),
                    "discount_usage": customer.get("discount_usage", 0),
                    "gross_margin": customer.get("gross_margin", 0),
                    "website_sessions": customer.get("website_sessions", 0),
                    "email_engagement": customer.get("email_engagement", 0),
                    "product_views": customer.get("product_views", 0),
                    "category_diversity": customer.get("category_diversity", 0),
                    "purchase_interval": customer.get("purchase_interval", 0),
                    "customer_segment": customer.get("customer_segment", "unknown"),
                    "health_score": customer.get("health_score", 0),
                    "loyalty_score": customer.get("loyalty_score", 0),
                    "satisfaction_score": customer.get("satisfaction_score", 0),
                    "churn_probability": customer.get("churn_probability", 0),
                    "rfm_score": customer.get("rfm_score", 0),
                    "region": customer.get("region", "unknown"),
                    "customer_type": customer.get("customer_type", "unknown"),
                    "industry": customer.get("industry", "unknown"),
                    "acquisition_channel": customer.get("acquisition_channel", "unknown"),
                    "target_clv": customer.get("target_clv", 0),
                }
            )
        return dataset
