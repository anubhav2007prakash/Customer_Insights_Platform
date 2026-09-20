"""SQLAlchemy Unit of Work implementation."""

from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session

from core.interfaces.unit_of_work import UnitOfWork
from core.logging.logger import LoggerMixin
from database.session import SessionLocal


class SQLAlchemyUnitOfWork(UnitOfWork, LoggerMixin):
    """Transaction boundary wrapping a SQLAlchemy session."""

    def __init__(self, session_factory=SessionLocal) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("UnitOfWork not started. Use 'with' context manager.")
        return self._session

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self.logger.debug("Transaction started")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type:
                self.rollback()
            else:
                self.commit()
        finally:
            if self._session:
                self._session.close()
                self._session = None

    def commit(self) -> None:
        if self._session:
            self._session.commit()
            self.logger.debug("Transaction committed")

    def rollback(self) -> None:
        if self._session:
            self._session.rollback()
            self.logger.debug("Transaction rolled back")
