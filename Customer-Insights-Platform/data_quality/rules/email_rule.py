"""Built-in validation rule for email fields."""
from __future__ import annotations

import re
from data_quality.rules.core import DataQualityRule


class EmailFormatRule(DataQualityRule):
    @property
    def name(self) -> str:
        return "EmailFormatRule"

    def validate(self, row: dict) -> dict:
        email = row.get("email")
        if email is None:
            return {"passed": False, "reason": "Email is missing."}

        pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        passed = bool(pattern.match(str(email)))
        return {
            "passed": passed,
            "reason": None if passed else "Invalid email format.",
            "value": email,
        }
