"""Simple mapping template storage using DB models."""
from __future__ import annotations

from typing import Dict
from ingestion.repositories.repository import IngestionRepository


class MappingTemplates:
    def __init__(self, repo: IngestionRepository | None = None):
        self.repo = repo or IngestionRepository()

    def save_template(self, organization_id, name: str, mapping: Dict[str, str]):
        # store in repo as metadata on a job stub or a dedicated table (simple JSON)
        # For brevity, reuse ImportJob.metadata_
        job = self.repo.create_job(organization_id=organization_id, file_name=f"template:{name}", source="mapping_template", user_id=None, status="saved", metadata_=mapping)
        return job

    def load_template(self, organization_id, name: str):
        # naive load
        return None
