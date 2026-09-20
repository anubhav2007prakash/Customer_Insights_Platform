"""Manage data and schema versions for datasets."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict

from data_quality.repositories.repository import DataQualityRepository
from data_quality.repositories.models import DataVersion


class VersionManager:
    def __init__(self, repository: DataQualityRepository | None = None):
        self.repository = repository or DataQualityRepository()

    def create_version(
        self,
        organization_id,
        dataset_name: str,
        import_version: int,
        schema_version: int,
        transformation_version: int,
        validation_version: int,
    ) -> DataVersion:
        normalized_org_id = uuid.UUID(str(organization_id)) if not isinstance(organization_id, uuid.UUID) else organization_id
        version = DataVersion(
            organization_id=normalized_org_id,
            dataset_name=dataset_name,
            import_version=import_version,
            schema_version=schema_version,
            transformation_version=transformation_version,
            validation_version=validation_version,
            created_at=datetime.utcnow(),
        )
        return self.repository.add_data_version(version)
