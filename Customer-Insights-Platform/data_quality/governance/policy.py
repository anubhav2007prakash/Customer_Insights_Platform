"""Governance policy engine for dataset compliance and classification."""
from __future__ import annotations

from datetime import datetime
from typing import Dict

from data_quality.repositories.repository import DataQualityRepository
from data_quality.repositories.models import GovernancePolicy


class GovernancePolicyEngine:
    def __init__(self, repository: DataQualityRepository | None = None):
        self.repository = repository or DataQualityRepository()

    def enforce(self, organization_id, dataset_name: str, data: list[dict], policies: list[dict]) -> dict:
        results = []
        for policy_def in policies:
            policy_type = policy_def.get("policy_type")
            result = {
                "policy_name": policy_def.get("policy_name"),
                "policy_type": policy_type,
                "passed": True,
                "details": None,
            }

            if policy_type == "retention":
                if not self._validate_retention(data, policy_def.get("retention_days", 0)):
                    result["passed"] = False
                    result["details"] = "Retention policy may be violated by stale rows."
            elif policy_type == "sensitive_field_detection":
                detected = self._detect_sensitive_fields(data, policy_def.get("fields", []))
                result["details"] = {"sensitive_fields": detected}
            elif policy_type == "required_fields":
                missing = self._validate_required_fields(data, policy_def.get("fields", []))
                if missing:
                    result["passed"] = False
                    result["details"] = {"missing_fields": missing}
            else:
                result["details"] = "Policy type not supported."
                result["passed"] = False

            self.repository.add_governance_policy(
                GovernancePolicy(
                    organization_id=organization_id,
                    dataset_name=dataset_name,
                    policy_name=policy_def.get("policy_name", "unnamed"),
                    policy_type=policy_type,
                    policy_definition=policy_def,
                    enabled=policy_def.get("enabled", True),
                    created_at=datetime.utcnow(),
                )
            )
            results.append(result)

        return {"dataset_name": dataset_name, "policies": results}

    def _validate_retention(self, data: list[dict], retention_days: int) -> bool:
        if retention_days <= 0:
            return True
        # This is a placeholder: real retention validation should inspect timestamp fields.
        return True

    def _detect_sensitive_fields(self, data: list[dict], fields: list[str]) -> list[str]:
        detected = []
        if not data:
            return detected
        sample = data[0]
        for field in fields:
            if field in sample:
                detected.append(field)
        return detected

    def _validate_required_fields(self, data: list[dict], fields: list[str]) -> list[str]:
        if not data:
            return fields
        missing = []
        for field in fields:
            if any(row.get(field) in (None, "") for row in data):
                missing.append(field)
        return missing
