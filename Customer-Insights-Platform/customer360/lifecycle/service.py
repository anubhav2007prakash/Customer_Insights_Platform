"""Lifecycle stage management for customer 360."""
from __future__ import annotations

from typing import Any


class LifecycleService:
    def __init__(self):
        self.default_stages = [
            "visitor",
            "lead",
            "prospect",
            "first_time_customer",
            "active_customer",
            "repeat_customer",
            "loyal_customer",
            "vip_customer",
            "at_risk_customer",
            "churned_customer",
            "re_activated_customer",
        ]

    def get_stage(self, profile: Any) -> str:
        return getattr(profile, "profile_status", "active")

    def update_stage(self, profile: Any, stage: str) -> str:
        profile.profile_status = stage
        return stage
