"""Dependency injection container."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from core.config.settings import Settings, get_settings
from core.events.bus import InMemoryEventBus
from core.interfaces.cache import CachePort
from core.interfaces.event_bus import EventBusPort
from core.interfaces.unit_of_work import UnitOfWork
from infrastructure.cache.memory_cache import InMemoryCache
from infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork

T = TypeVar("T")


@dataclass
class Container:
    """
    Application dependency injection container.

    Wire dependencies at startup; inject into services and presentation layer.
    """

    settings: Settings = field(default_factory=get_settings)
    _singletons: dict[type, Any] = field(default_factory=dict)
    _factories: dict[type, Callable[[], Any]] = field(default_factory=dict)

    def register_singleton(self, interface: type[T], instance: T) -> None:
        """Register a pre-created singleton instance."""
        self._singletons[interface] = instance

    def register_factory(self, interface: type[T], factory: Callable[[], T]) -> None:
        """Register a factory for lazy instantiation."""
        self._factories[interface] = factory

    def resolve(self, interface: type[T]) -> T:
        """Resolve a dependency by interface type."""
        if interface in self._singletons:
            return self._singletons[interface]
        if interface in self._factories:
            instance = self._factories[interface]()
            self._singletons[interface] = instance
            return instance
        raise KeyError(f"No registration for {interface.__name__}")

    def wire_defaults(self) -> None:
        """Register default infrastructure implementations."""
        self.register_singleton(Settings, self.settings)
        self.register_factory(EventBusPort, InMemoryEventBus)
        self.register_factory(CachePort, InMemoryCache)
        self.register_factory(UnitOfWork, SQLAlchemyUnitOfWork)


_container: Container | None = None


def get_container() -> Container:
    """Return the global DI container (lazy init)."""
    global _container
    if _container is None:
        _container = Container()
        _container.wire_defaults()
    return _container


def reset_container() -> None:
    """Reset container — for testing only."""
    global _container
    _container = None
