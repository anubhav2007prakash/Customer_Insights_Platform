"""Schema version management and evolution tracking."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict

from data_quality.repositories.repository import DataQualityRepository
from data_quality.repositories.models import SchemaDefinition, SchemaVersion


class SchemaVersionManager:
    def __init__(self, repository: DataQualityRepository | None = None):
        self.repository = repository or DataQualityRepository()

    def create_definition(self, organization_id: uuid.UUID | str, dataset_name: str, schema_spec: dict, overrides: dict | None = None) -> SchemaDefinition:
        normalized_org_id = uuid.UUID(str(organization_id)) if not isinstance(organization_id, uuid.UUID) else organization_id
        schema_def = SchemaDefinition(
            organization_id=normalized_org_id,
            dataset_name=dataset_name,
            version_id=uuid.uuid4(),
            schema_spec=schema_spec,
            manual_overrides=overrides or {},
            detected_at=datetime.utcnow(),
        )
        return self.repository.add_schema_definition(schema_def)

    def create_version(self, organization_id: uuid.UUID | str, schema_definition_id: uuid.UUID, schema_spec: dict, change_summary: str) -> SchemaVersion:
        normalized_org_id = uuid.UUID(str(organization_id)) if not isinstance(organization_id, uuid.UUID) else organization_id
        version = SchemaVersion(
            organization_id=normalized_org_id,
            schema_definition_id=schema_definition_id,
            version=self._next_version(schema_definition_id),
            change_summary=change_summary,
            schema_spec=schema_spec,
            created_at=datetime.utcnow(),
        )
        return self.repository.add_schema_version(version)

    def _next_version(self, schema_definition_id: uuid.UUID) -> int:
        # This is a placeholder. A real implementation would query the repository for latest version.
        return 1
