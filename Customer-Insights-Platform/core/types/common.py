"""Shared type aliases and DTO primitives."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar("T")

OrganizationId = uuid.UUID
UserId = uuid.UUID
CustomerId = uuid.UUID
WorkspaceId = uuid.UUID


@dataclass(frozen=True)
class TenantContext:
    """Multi-tenant request context propagated through all layers."""

    organization_id: OrganizationId
    user_id: UserId | None = None
    workspace_id: WorkspaceId | None = None
    roles: tuple[str, ...] = field(default_factory=tuple)
    permissions: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class PaginationParams:
    """Standard pagination input."""

    page: int = 1
    page_size: int = 50

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if not 1 <= self.page_size <= 500:
            raise ValueError("page_size must be between 1 and 500")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


@dataclass(frozen=True)
class PaginatedResult(Generic[T]):
    """Standard paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def pages(self) -> int:
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.pages


@dataclass(frozen=True)
class SortParams:
    """Standard sorting input."""

    sort_by: str = "created_at"
    sort_order: str = "desc"

    def __post_init__(self) -> None:
        if self.sort_order not in ("asc", "desc"):
            raise ValueError("sort_order must be 'asc' or 'desc'")


@dataclass(frozen=True)
class AuditMetadata:
    """Audit trail metadata attached to mutations."""

    actor_id: UserId | None
    timestamp: datetime
    ip_address: str | None = None
    user_agent: str | None = None
