"""Feedback handling for recommendation engine."""
from __future__ import annotations

from typing import Any


class FeedbackService:
    def __init__(self) -> None:
        self._feedback: list[dict[str, Any]] = []

    def record_feedback(self, customer_id: str, status: str) -> dict[str, Any]:
        entry = {"customer_id": customer_id, "status": status}
        self._feedback.append(entry)
        return entry

    def get_feedback(self, customer_id: str) -> list[dict[str, Any]]:
        return [entry for entry in self._feedback if entry.get("customer_id") == customer_id]
