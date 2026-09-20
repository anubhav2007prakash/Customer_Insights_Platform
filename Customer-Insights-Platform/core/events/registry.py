"""Event handler registration utilities."""

from __future__ import annotations

from typing import Callable, TypeVar

from core.events.base import DomainEvent
from core.interfaces.event_bus import EventBusPort, EventHandler

T = TypeVar("T", bound=DomainEvent)


class EventRegistry:
    """Collects event handler registrations for bootstrap."""

    def __init__(self) -> None:
        self._registrations: list[tuple[type[DomainEvent], EventHandler]] = []

    def register(self, event_type: type[T], handler: EventHandler) -> None:
        self._registrations.append((event_type, handler))

    def apply(self, bus: EventBusPort) -> None:
        for event_type, handler in self._registrations:
            bus.subscribe(event_type, handler)


def register_handler(
    registry: EventRegistry,
    event_type: type[T],
) -> Callable[[EventHandler], EventHandler]:
    """Decorator to register event handlers."""

    def decorator(handler: EventHandler) -> EventHandler:
        registry.register(event_type, handler)
        return handler

    return decorator
