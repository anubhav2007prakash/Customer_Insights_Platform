"""Load engine for writing processed data into PostgreSQL/SQLAlchemy target."""
from __future__ import annotations

from typing import Iterable, List
from ingestion.connectors.db.postgres_connector import PostgresConnector


class LoadError(Exception):
    pass


class LoadEngine:
    def __init__(self, url: str):
        self.connector = PostgresConnector(url)

    def load_table(self, table_name: str, rows: Iterable[dict], batch_size: int = 1000):
        try:
            self.connector.write_table(table_name, rows, batch_size=batch_size)
        except Exception as exc:
            raise LoadError(str(exc)) from exc
