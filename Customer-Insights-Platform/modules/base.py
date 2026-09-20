"""Base classes for bounded context modules."""

from __future__ import annotations

from abc import ABC

from core.interfaces.service import Service
from core.logging.logger import LoggerMixin


class BaseService(Service, LoggerMixin, ABC):
    """
    Base application service for all modules.

    Services receive repositories and infrastructure via constructor injection.
    Business rules live here — never in repositories or presentation layer.
    """

    pass


class BaseModuleRepository(ABC):
    """
    Marker for module-specific repositories.

    Extend `infrastructure.persistence.base_repository.SQLAlchemyRepository`.
    """

    pass
