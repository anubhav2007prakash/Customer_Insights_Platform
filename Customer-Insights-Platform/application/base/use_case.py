"""Base use case class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from core.interfaces.service import Service
from core.logging.logger import LoggerMixin
from core.types.common import TenantContext

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class UseCase(Service, LoggerMixin, ABC, Generic[InputT, OutputT]):
    """
    Application use case — single public operation per class.

    Flow: validate input → call service(s) → return output DTO.
    """

    @abstractmethod
    def execute(self, request: InputT, ctx: TenantContext) -> OutputT:
        """Execute the use case."""
