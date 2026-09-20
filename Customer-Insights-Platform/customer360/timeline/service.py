"""Timeline service for customer activity events."""
from __future__ import annotations

from datetime import datetime
from typing import Any


class TimelineService:
    def build_timeline(self, profile_id, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            [
                {
                    "profile_id": profile_id,
                    "event_type": event.get("event_type", "custom"),
                    "event_time": event.get("event_time", datetime.utcnow().isoformat()),
                    "details": event.get("details", {}),
                }
                for event in events
            ],
            key=lambda item: item["event_time"],
        )
