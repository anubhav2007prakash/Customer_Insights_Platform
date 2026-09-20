"""Dependency injection bridge for Streamlit pages.

CRITICAL: Streamlit pages must NEVER query the database directly.
All data access flows through services resolved from this module.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, TypeVar

from core.di.container import get_container
from core.exceptions.handlers import handle_exception
from core.interfaces.unit_of_work import UnitOfWork
from core.logging.logger import setup_logging

T = TypeVar("T")

_initialized = False


def _ensure_initialized() -> None:
    global _initialized
    if not _initialized:
        setup_logging()
        get_container().wire_defaults()
        _initialized = True


def get_service(service_type: type[T]) -> T:
    """
    Resolve an application service from the DI container.

    Usage in Streamlit pages:
        customer_service = get_service(CustomerService)
        result = customer_service.list_customers(ctx, pagination)
    """
    _ensure_initialized()
    return get_container().resolve(service_type)


@contextmanager
def with_uow() -> Generator[UnitOfWork, None, None]:
    """
    Provide a transactional unit of work for multi-step operations.

    Usage:
        with with_uow() as uow:
            service.do_something(uow.session)
            uow.commit()
    """
    _ensure_initialized()
    uow = get_container().resolve(UnitOfWork)
    with uow:
        yield uow


def safe_execute(func, *args, **kwargs):
    """
    Execute a presentation action with standardized error handling.

    Returns user-friendly message on failure.
    """
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        payload = handle_exception(exc)
        return payload
