"""Centralized logging setup and helpers."""

from __future__ import annotations

import logging
import sys
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Generator, TypeVar

from core.config.settings import Settings, get_settings
from core.logging.formatters import InsightForgeFormatter, JSONFormatter

F = TypeVar("F", bound=Callable[..., Any])

_CONFIGURED = False


def setup_logging(settings: Settings | None = None) -> None:
    """
    Configure application-wide logging once at startup.

    Args:
        settings: Optional settings override (useful in tests).
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    cfg = settings or get_settings()
    root = logging.getLogger("insightforge")
    root.setLevel(getattr(logging, cfg.logging.level))
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if cfg.logging.format == "json" or cfg.is_production:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(InsightForgeFormatter())
    root.addHandler(handler)

    if cfg.logging.file_path:
        file_handler = logging.FileHandler(cfg.logging.file_path)
        file_handler.setFormatter(JSONFormatter())
        root.addHandler(file_handler)

    if cfg.logging.enable_sql_logging:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger under insightforge.*."""
    if not name.startswith("insightforge"):
        name = f"insightforge.{name}"
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin providing a module-scoped logger to services."""

    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__module__)


def log_security_event(event: str, **data: Any) -> None:
    """Log a security-related event."""
    logger = get_logger("security")
    logger.warning("SECURITY_EVENT: %s | %s", event, data)


def log_ai_call(model: str, tokens: int, latency_ms: float, **data: Any) -> None:
    """Log AI inference calls."""
    logger = get_logger("ai")
    logger.info("AI_CALL model=%s tokens=%d latency_ms=%.1f data=%s", model, tokens, latency_ms, data)


@contextmanager
def log_performance(operation: str, **context: Any) -> Generator[None, None, None]:
    """Context manager to log operation duration."""
    logger = get_logger("performance")
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("PERF %s elapsed_ms=%.2f context=%s", operation, elapsed_ms, context)


def logged(operation: str | None = None) -> Callable[[F], F]:
    """Decorator to log function entry, exit, and errors."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger(func.__module__)
            op = operation or func.__name__
            logger.debug("Entering %s", op)
            try:
                result = func(*args, **kwargs)
                logger.debug("Completed %s", op)
                return result
            except Exception:
                logger.exception("Failed %s", op)
                raise

        return wrapper  # type: ignore[return-value]

    return decorator
