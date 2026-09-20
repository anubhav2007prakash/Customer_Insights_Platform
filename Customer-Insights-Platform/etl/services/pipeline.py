"""Core ETL Pipeline Engine orchestrating stages and runs."""
from __future__ import annotations

import time
import logging
from typing import Iterable, Dict, Any, List

from etl.transform.transformer import Transformer, TransformationError
from etl.repositories.repository import ETLRepository
from etl.normalizers.normalizer import normalize_email, normalize_phone
from etl.dedup.deduplicator import deduplicate
from etl.enrich.enricher import enrich_batch
from etl.load.loader import LoadEngine, LoadError

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    pass


class PipelineEngine:
    def __init__(self, organization_id, load_url: str):
        self.organization_id = organization_id
        self.load_engine = LoadEngine(load_url)
        self.repo = ETLRepository()

    def run(self, rows: Iterable[dict], transformation_spec: List[dict] | None = None, dedup_keys: List[str] | None = None, dedup_strategy: str = "keep_first", target_table: str | None = None, batch_size: int = 1000, retry: int = 3) -> Dict[str, Any]:
        start = time.time()
        # persist job/run
        job = self.repo.create_job(organization_id=self.organization_id, trigger="manual", status="queued")
        run = self.repo.start_run(organization_id=self.organization_id, job_id=job.id)
        metrics = {"total": 0, "processed": 0, "failed": 0}
        errors: List[Dict] = []

        # stage: transform
        transformer = Transformer(transformation_spec or [])
        transformed = []
        for idx, r in enumerate(rows):
            metrics["total"] += 1
            try:
                t = transformer.apply(r)
                transformed.append(t)
            except TransformationError as exc:
                metrics["failed"] += 1
                errors.append({"index": idx, "error": str(exc), "row": r})

        # stage: normalize
        normalized = []
        for r in transformed:
            r["email"] = normalize_email(r.get("email"))
            r["phone"] = normalize_phone(r.get("phone"))
            normalized.append(r)

        # stage: deduplicate
        if dedup_keys:
            deduped, duplicates = deduplicate(normalized, dedup_keys, strategy=dedup_strategy)
        else:
            deduped = normalized
            duplicates = []

        # stage: enrich
        enriched = enrich_batch(deduped)

        # stage: load
        if target_table:
            attempt = 0
            while attempt <= retry:
                try:
                    self.load_engine.load_table(target_table, enriched, batch_size=batch_size)
                    break
                except LoadError as exc:
                    attempt += 1
                    logger.exception("Load attempt %s failed", attempt)
                    if attempt > retry:
                        raise PipelineError("Load failed after retries") from exc

        duration = time.time() - start
        metrics.update({"processed": len(enriched), "duplicates": len(duplicates), "duration_seconds": duration})

        # persist metrics and mark run complete
        self.repo.complete_run(run, metrics)
        self.repo.add_audit(self.organization_id, run.id, "pipeline_completed", {"metrics": metrics})

        return {"metrics": metrics, "errors": errors, "duplicates": duplicates}
