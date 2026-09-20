"""Repository port interfaces."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from core.types.common import PaginatedResult, PaginationParams, SortParams, TenantContext

T = TypeVar("T")
ID = TypeVar("ID", bound=uuid.UUID)


class ReadRepository(ABC, Generic[T, ID]):
    """Read-only repository port."""

    @abstractmethod
    def get_by_id(self, entity_id: ID, ctx: TenantContext) -> T | None:
        """Fetch a single entity by primary key."""

    @abstractmethod
    def list(
        self,
        ctx: TenantContext,
        pagination: PaginationParams,
        sort: SortParams | None = None,
        **filters: object,
    ) -> PaginatedResult[T]:
        """List entities with pagination, sorting, and filters."""

    @abstractmethod
    def count(self, ctx: TenantContext, **filters: object) -> int:
        """Count entities matching filters."""

    @abstractmethod
    def exists(self, entity_id: ID, ctx: TenantContext) -> bool:
        """Check entity existence."""


class WriteRepository(ABC, Generic[T, ID]):
    """Write repository port."""

    @abstractmethod
    def create(self, entity: T, ctx: TenantContext) -> T:
        """Persist a new entity."""

    @abstractmethod
    def update(self, entity: T, ctx: TenantContext) -> T:
        """Update an existing entity."""

    @abstractmethod
    def delete(self, entity_id: ID, ctx: TenantContext) -> None:
        """Soft-delete an entity."""


class Repository(ReadRepository[T, ID], WriteRepository[T, ID], ABC):
    """Full CRUD repository port combining read and write operations."""

    @abstractmethod
    def search(self, query: str, ctx: TenantContext, pagination: PaginationParams) -> PaginatedResult[T]:
        """Full-text or field search."""
