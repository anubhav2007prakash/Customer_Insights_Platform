"""K-Means based clustering service for segmentation."""
from __future__ import annotations

from typing import Any


class KMeansSegmentationService:
    def predict(self, customers: list[dict[str, Any]], model: dict[str, Any]) -> list[dict[str, Any]]:
        clusters = []
        for index, customer in enumerate(customers):
            cluster_id = (index % int(model.get("cluster_count", 1))) + 1
            clusters.append({"customer_id": customer.get("customer_id"), "cluster_id": cluster_id})
        return clusters
