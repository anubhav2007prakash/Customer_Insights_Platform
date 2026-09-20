"""Simple transformation pipeline supporting chained operations."""
from __future__ import annotations

from typing import Callable, Iterable


class TransformPipeline:
    def __init__(self, steps: Iterable[Callable[[dict], dict]] | None = None):
        self.steps = list(steps or [])

    def add_step(self, fn: Callable[[dict], dict]):
        self.steps.append(fn)

    def run(self, rows: Iterable[dict]):
        for r in rows:
            out = r
            for s in self.steps:
                out = s(out)
            yield out
