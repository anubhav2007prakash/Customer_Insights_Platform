"""Assignment service for segment labels."""
from __future__ import annotations

from typing import Any


class AssignmentService:
    def assign(self, customers: list[dict[str, Any]], cluster_assignments: Any) -> list[dict[str, Any]]:
        segment_id = cluster_assignments if isinstance(cluster_assignments, str) else None
        assignment_map = {}
        if isinstance(cluster_assignments, list):
            assignment_map = {item.get("customer_id"): item.get("cluster_id") for item in cluster_assignments}

        assigned = []
        for customer in customers:
            customer_id = customer.get("customer_id")
            assigned.append(
                {
                    "customer_id": customer_id,
                    "cluster_id": assignment_map.get(customer_id),
                    "segment_id": segment_id or assignment_map.get(customer_id),
                }
            )
        return assigned
