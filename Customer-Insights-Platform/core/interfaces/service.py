"""Service layer port interface."""

from __future__ import annotations

from abc import ABC


class Service(ABC):
    """
    Marker base class for application services.

    Services encapsulate business rules, orchestration, and cross-cutting concerns.
    They must never perform direct SQL or ORM operations.
    """
