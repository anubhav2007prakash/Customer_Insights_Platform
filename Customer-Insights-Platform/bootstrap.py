"""Application bootstrap — initialize backend on startup."""

from __future__ import annotations

from core.config.settings import Settings, get_settings
from core.di.container import get_container, reset_container
from core.events.registry import EventRegistry
from core.interfaces.event_bus import EventBusPort
from core.logging.logger import get_logger, setup_logging

logger = get_logger("bootstrap")


def bootstrap(settings: Settings | None = None) -> None:
    """
    Initialize the backend application.

    Call once at application entry (app.py) before serving requests.
    """
    cfg = settings or get_settings()
    setup_logging(cfg)
    container = get_container()
    container.settings = cfg
    container.wire_defaults()
    _register_event_handlers(container)
    logger.info(
        "InsightForge AI backend initialized | env=%s version=%s",
        cfg.environment.value,
        cfg.app_version,
    )


def _register_event_handlers(container) -> None:
    """Register domain event handlers from modules."""
    registry = EventRegistry()
    # Module handlers register here as implemented:
    # from modules.customer.events import register_customer_handlers
    # register_customer_handlers(registry)
    registry.apply(container.resolve(EventBusPort))


def shutdown() -> None:
    """Clean shutdown — reset DI container (testing/dev)."""
    logger.info("Shutting down backend")
    reset_container()
