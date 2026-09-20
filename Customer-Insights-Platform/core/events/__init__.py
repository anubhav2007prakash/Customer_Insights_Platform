"""Internal domain event system."""

from core.events.base import DomainEvent, EventMetadata
from core.events.bus import InMemoryEventBus
from core.events.registry import EventRegistry, register_handler

__all__ = [
    "DomainEvent",
    "EventMetadata",
    "InMemoryEventBus",
    "EventRegistry",
    "register_handler",
]
