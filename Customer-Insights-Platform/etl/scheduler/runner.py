"""Scheduler wrapper for ETL pipelines using APScheduler."""
from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable


class ETLScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def start(self):
        self.scheduler.start()

    def add_cron(self, fn: Callable, cron_expr: str, **kwargs):
        trigger = CronTrigger.from_crontab(cron_expr)
        self.scheduler.add_job(fn, trigger, kwargs=kwargs)

    def shutdown(self):
        self.scheduler.shutdown(wait=False)
