"""Structured logger for ETL with JSON-friendly entries."""
from __future__ import annotations

import logging
import json


class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, event: str, **kwargs):
        self.logger.info(json.dumps({"event": event, **kwargs}))

    def error(self, event: str, **kwargs):
        self.logger.error(json.dumps({"event": event, **kwargs}))
