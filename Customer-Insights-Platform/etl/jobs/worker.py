"""Simple background job queue and worker for ETL jobs."""
from __future__ import annotations

import threading
import queue
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


class JobWorker:
    def __init__(self, concurrency: int = 2):
        self.q: queue.Queue = queue.Queue()
        self.threads = []
        self.concurrency = concurrency
        self._stop = threading.Event()

    def start(self):
        for _ in range(self.concurrency):
            t = threading.Thread(target=self._run_loop, daemon=True)
            t.start()
            self.threads.append(t)

    def _run_loop(self):
        while not self._stop.is_set():
            try:
                func, args, kwargs = self.q.get(timeout=1)
            except Exception:
                continue
            try:
                func(*args, **kwargs)
            except Exception:
                logger.exception("Job failed")
            finally:
                self.q.task_done()

    def submit(self, fn: Callable[..., Any], *args, **kwargs):
        self.q.put((fn, args, kwargs))

    def stop(self):
        self._stop.set()
        for t in self.threads:
            t.join(timeout=1)
