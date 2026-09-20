"""SQLAlchemy engine and session factory."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from database.connection import DatabaseConfig

_config = DatabaseConfig.from_env()

engine = create_engine(
    _config.sync_url,
    pool_size=_config.pool_size,
    max_overflow=_config.max_overflow,
    pool_timeout=_config.pool_timeout,
    pool_recycle=_config.pool_recycle,
    echo=_config.echo,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


@event.listens_for(engine, "connect")
def _set_pg_options(dbapi_connection, connection_record) -> None:
    """Set PostgreSQL session defaults for analytics workloads."""
    cursor = dbapi_connection.cursor()
    cursor.execute("SET TIME ZONE 'UTC'")
    cursor.close()


def get_session() -> Generator[Session, None, None]:
    """FastAPI/Streamlit dependency-style session yielder."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager for scripts and batch jobs."""
    yield from get_session()
