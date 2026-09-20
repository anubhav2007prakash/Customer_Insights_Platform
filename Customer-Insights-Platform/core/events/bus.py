"""In-memory event bus implementation."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from core.events.base import DomainEvent
from core.interfaces.event_bus import EventBusPort, EventHandler
from core.logging.logger import get_logger

logger = get_logger("events")


class InMemoryEventBus(EventBusPort):
    """
    Synchronous in-process event bus.

    Replace with message queue adapter (Redis, RabbitMQ, Kafka) in production scale-out.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def publish(self, event: DomainEvent) -> None:
        """Publish event to all registered handlers."""
        logger.debug("Publishing event: %s", event.event_name)
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception("Event handler failed for %s", event.event_name)

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Register handler."""
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.debug("Subscribed %s to %s", handler.__name__, event_type.__name__)

    def unsubscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Remove handler."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
