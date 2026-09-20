"""Event bus port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, TypeVar

from core.events.base import DomainEvent

T = TypeVar("T", bound=DomainEvent)
EventHandler = Callable[[DomainEvent], None]


class EventBusPort(ABC):
    """Publish/subscribe event bus port."""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to all registered handlers."""

    @abstractmethod
    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Register a handler for an event type."""

    @abstractmethod
    def unsubscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Remove a handler registration."""
