"""Aggregate root base class."""

from __future__ import annotations

from dataclasses import dataclass, field

from core.events.base import DomainEvent
from domain.base.entity import DomainEntity


@dataclass
class AggregateRoot(DomainEntity):
    """
    Aggregate root — consistency boundary for domain events.

    Collect events during business operations; publish after commit.
    """

    _events: list[DomainEvent] = field(default_factory=list, repr=False, compare=False)

    def record_event(self, event: DomainEvent) -> None:
        """Record a domain event for later publication."""
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        """Return and clear pending domain events."""
        events = list(self._events)
        self._events.clear()
        return events
