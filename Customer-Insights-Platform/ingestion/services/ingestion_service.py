"""Core ingestion orchestration service implementing the import workflow."""
from __future__ import annotations

import hashlib
import io
import json
import time
from typing import Dict, Iterable, List, Any

from ingestion.parsers.csv_parser import parse_csv
from ingestion.parsers.json_parser import parse_json
from ingestion.parsers.excel_parser import parse_excel
from ingestion.validators.validator import validate_stream
from ingestion.mappers.mapper import auto_map_columns, apply_mapping
from ingestion.cleaners.cleaner import trim_spaces, normalize_case, standardize_dates
from ingestion.repositories.repository import IngestionRepository
from ingestion.schemas import UploadResult, ValidationReport
from ingestion.transformers.pipeline import TransformPipeline
from ingestion.mapping.templates import MappingTemplates


class IngestionService:
    def __init__(self, repo: IngestionRepository | None = None):
        self.repo = repo or IngestionRepository()

    def _hash_file(self, file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    def preview(self, file_bytes: bytes, filename: str, max_rows: int = 10):
        """Return a small preview (list of dicts) for supported file types."""
        lower = filename.lower()
        if lower.endswith(".csv"):
            f = io.StringIO(file_bytes.decode("utf-8", errors="replace"))
            rows = []
            for r in parse_csv(f):
                rows.append(r)
                if len(rows) >= max_rows:
                    break
            return UploadResult(file_name=filename, preview=rows, checksum=self._hash_file(file_bytes))

        if lower.endswith(".json"):
            f = io.StringIO(file_bytes.decode("utf-8", errors="replace"))
            rows = []
            for r in parse_json(f):
                rows.append(r)
                if len(rows) >= max_rows:
                    break
            return UploadResult(file_name=filename, preview=rows, checksum=self._hash_file(file_bytes))

        if lower.endswith(('.xls', '.xlsx')):
            f = io.BytesIO(file_bytes)
            rows = []
            for r in parse_excel(f):
                rows.append(r)
                if len(rows) >= max_rows:
                    break
            return UploadResult(file_name=filename, preview=rows, checksum=self._hash_file(file_bytes))

        raise ValueError("Unsupported file type for preview")

    def import_file(self, organization_id, user_id, file_bytes: bytes, filename: str, mapping: Dict[str, str] | None = None, required: Iterable[str] = ()):  # noqa: D401
        start = time.time()
        job = self.repo.create_job(organization_id=organization_id, file_name=filename, source="upload", user_id=user_id, status="started")

        try:
            lower = filename.lower()
            if lower.endswith('.csv'):
                f = io.StringIO(file_bytes.decode('utf-8', errors='replace'))
                rows_iter = parse_csv(f)
            elif lower.endswith('.json'):
                f = io.StringIO(file_bytes.decode('utf-8', errors='replace'))
                rows_iter = parse_json(f)
            elif lower.endswith(('.xls', '.xlsx')):
                f = io.BytesIO(file_bytes)
                rows_iter = parse_excel(f)
            else:
                raise ValueError('Unsupported file type')

            # validation
            report = validate_stream(rows_iter, required=required)

            # For import we need to re-iterate rows: re-parse
            if lower.endswith('.csv'):
                f.seek(0)
                rows_iter = parse_csv(f)
            elif lower.endswith('.json'):
                f.seek(0)
                rows_iter = parse_json(f)
            elif lower.endswith(('.xls', '.xlsx')):
                f = io.BytesIO(file_bytes)
                rows_iter = parse_excel(f)

            # mapping
            first_row = None
            rows_buffer = []
            for i, r in enumerate(rows_iter):
                if i == 0:
                    first_row = r
                rows_buffer.append(r)

            if mapping is None and first_row is not None:
                # try to auto-map to common fields (email,name,phone)
                mapping = auto_map_columns(first_row.keys(), ["email", "name", "phone"]) or {}

            # load mapping templates helper
            templates = MappingTemplates(self.repo)

            # base transform pipeline
            pipeline = TransformPipeline()
            pipeline.add_step(trim_spaces)
            pipeline.add_step(normalize_case)

            # cleaning, mapping and (placeholder) write
            success = 0
            failed = 0
            for idx, row in enumerate(pipeline.run(rows_buffer)):
                # date fields autodetect
                date_fields = [k for k in row.keys() if k.lower().endswith('date')]
                row = standardize_dates(row, date_fields)

                # apply mapping
                r_mapped = apply_mapping(row, mapping) if mapping else row

                # TODO: insert into target systems; placeholder: count as success
                success += 1

            duration = int(time.time() - start)
            self.repo.update_job_counts(job, success=success, failed=failed, record_count=success+failed)
            job.status = 'completed'
            job.duration_seconds = duration
            self.repo.add_audit(job, 'import_completed', {'success': success, 'failed': failed}, user_id=user_id)

            return ValidationReport(total=report['total'], passed=report['passed'], failed=report['failed'], errors=report['errors'])

        except Exception:
            job.status = 'failed'
            self.repo.add_audit(job, 'import_failed', {'error': 'see logs'}, user_id=user_id)
            raise
