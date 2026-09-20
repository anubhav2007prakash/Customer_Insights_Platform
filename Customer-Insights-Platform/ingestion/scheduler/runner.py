"""APScheduler runner with retry/backoff support for ingestion jobs."""
from __future__ import annotations

import time
import logging
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class SchedulerRunner:
    def __init__(self):
        executors = {"default": ThreadPoolExecutor(10)}
        self.scheduler = BackgroundScheduler(executors=executors)

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown(wait=False)

    def add_job_with_retry(self, func: Callable, trigger: dict, max_retries: int = 3, backoff_seconds: int = 10, **kwargs):
        def _wrapped(*a, **kw):
            attempts = 0
            while attempts <= max_retries:
                try:
                    return func(*a, **kw)
                except Exception as exc:
                    attempts += 1
                    logger.exception("Job failed, attempt %s", attempts)
                    if attempts > max_retries:
                        raise
                    time.sleep(backoff_seconds * attempts)

        self.scheduler.add_job(_wrapped, **trigger, kwargs=kwargs)
