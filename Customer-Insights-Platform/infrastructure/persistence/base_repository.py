"""SQLAlchemy repository base implementation."""

from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from core.exceptions.base import DatabaseError, NotFoundError
from core.interfaces.repository import Repository
from core.logging.logger import LoggerMixin
from core.types.common import PaginatedResult, PaginationParams, SortParams, TenantContext

ORM = TypeVar("ORM")
Domain = TypeVar("Domain")

ID = TypeVar("ID", bound=uuid.UUID)


class SQLAlchemyRepository(Repository[Domain, ID], LoggerMixin, Generic[Domain, ID, ORM]):
    """
    Generic SQLAlchemy repository base.

    Subclasses implement `_to_domain`, `_to_orm`, and set `model_class`.
    """

    model_class: type[ORM]
    soft_delete_field: str = "deleted_at"

    def __init__(self, session: Session) -> None:
        self._session = session

    def _base_query(self, ctx: TenantContext) -> Select:
        """Build tenant-scoped base query. Override for custom scoping."""
        stmt = select(self.model_class)
        if hasattr(self.model_class, "organization_id"):
            stmt = stmt.where(self.model_class.organization_id == ctx.organization_id)  # type: ignore[attr-defined]
        if hasattr(self.model_class, self.soft_delete_field):
            stmt = stmt.where(getattr(self.model_class, self.soft_delete_field).is_(None))  # type: ignore[attr-defined]
        return stmt

    def _to_domain(self, orm_obj: ORM) -> Domain:
        raise NotImplementedError

    def _to_orm(self, domain: Domain) -> ORM:
        raise NotImplementedError

    def get_by_id(self, entity_id: ID, ctx: TenantContext) -> Domain | None:
        stmt = self._base_query(ctx).where(self.model_class.id == entity_id)  # type: ignore[attr-defined]
        orm_obj = self._session.scalars(stmt).first()
        return self._to_domain(orm_obj) if orm_obj else None

    def list(
        self,
        ctx: TenantContext,
        pagination: PaginationParams,
        sort: SortParams | None = None,
        **filters: object,
    ) -> PaginatedResult[Domain]:
        stmt = self._apply_filters(self._base_query(ctx), **filters)
        total = self._session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        if sort and hasattr(self.model_class, sort.sort_by):
            col = getattr(self.model_class, sort.sort_by)
            stmt = stmt.order_by(col.desc() if sort.sort_order == "desc" else col.asc())
        stmt = stmt.offset(pagination.offset).limit(pagination.limit)
        items = [self._to_domain(o) for o in self._session.scalars(stmt).all()]
        return PaginatedResult(items=items, total=total, page=pagination.page, page_size=pagination.page_size)

    def count(self, ctx: TenantContext, **filters: object) -> int:
        stmt = self._apply_filters(self._base_query(ctx), **filters)
        return self._session.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    def exists(self, entity_id: ID, ctx: TenantContext) -> bool:
        return self.get_by_id(entity_id, ctx) is not None

    def create(self, entity: Domain, ctx: TenantContext) -> Domain:
        try:
            orm_obj = self._to_orm(entity)
            self._session.add(orm_obj)
            self._session.flush()
            return self._to_domain(orm_obj)
        except Exception as exc:
            self.logger.exception("Create failed")
            raise DatabaseError(cause=exc) from exc

    def update(self, entity: Domain, ctx: TenantContext) -> Domain:
        try:
            orm_obj = self._to_orm(entity)
            merged = self._session.merge(orm_obj)
            self._session.flush()
            return self._to_domain(merged)
        except Exception as exc:
            self.logger.exception("Update failed")
            raise DatabaseError(cause=exc) from exc

    def delete(self, entity_id: ID, ctx: TenantContext) -> None:
        orm_obj = self._session.scalars(
            self._base_query(ctx).where(self.model_class.id == entity_id)  # type: ignore[attr-defined]
        ).first()
        if not orm_obj:
            raise NotFoundError(details={"id": str(entity_id)})
        if hasattr(orm_obj, self.soft_delete_field):
            from datetime import datetime, timezone
            setattr(orm_obj, self.soft_delete_field, datetime.now(timezone.utc))
        else:
            self._session.delete(orm_obj)
        self._session.flush()

    def search(self, query: str, ctx: TenantContext, pagination: PaginationParams) -> PaginatedResult[Domain]:
        raise NotImplementedError("Override in subclass with field-specific search.")

    def _apply_filters(self, stmt: Select, **filters: object) -> Select:
        for key, value in filters.items():
            if value is not None and hasattr(self.model_class, key):
                stmt = stmt.where(getattr(self.model_class, key) == value)
        return stmt
