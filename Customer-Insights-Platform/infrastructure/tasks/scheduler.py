"""Background task scheduler port and stub."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable


@dataclass
class ScheduledTask:
    """Represents a schedulable background job."""

    name: str
    handler: Callable[..., Any]
    cron: str | None = None
    run_at: datetime | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)


class TaskSchedulerPort(ABC):
    """Port for background task scheduling (Celery, APScheduler, etc.)."""

    @abstractmethod
    def schedule(self, task: ScheduledTask) -> str:
        """Schedule a task; returns task ID."""

    @abstractmethod
    def cancel(self, task_id: str) -> None:
        """Cancel a scheduled task."""


class InMemoryTaskScheduler(TaskSchedulerPort):
    """In-memory scheduler stub for architecture validation."""

    def __init__(self) -> None:
        self._tasks: deque[ScheduledTask] = deque()
        self._ids: dict[str, ScheduledTask] = {}

    def schedule(self, task: ScheduledTask) -> str:
        import uuid
        task_id = str(uuid.uuid4())
        self._tasks.append(task)
        self._ids[task_id] = task
        return task_id

    def cancel(self, task_id: str) -> None:
        self._ids.pop(task_id, None)
