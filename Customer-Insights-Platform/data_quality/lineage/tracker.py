"""Track dataset lineage for governance and auditability."""
from __future__ import annotations

from datetime import datetime
from typing import Dict

from data_quality.repositories.repository import DataQualityRepository
from data_quality.repositories.models import LineageRecord


class LineageTracker:
    def __init__(self, repository: DataQualityRepository | None = None):
        self.repository = repository or DataQualityRepository()

    def capture(self, organization_id, dataset_name: str, lineage: Dict[str, object]) -> LineageRecord:
        record = LineageRecord(
            organization_id=organization_id,
            dataset_name=dataset_name,
            lineage=lineage,
            captured_at=datetime.utcnow(),
        )
        return self.repository.add_lineage_record(record)
