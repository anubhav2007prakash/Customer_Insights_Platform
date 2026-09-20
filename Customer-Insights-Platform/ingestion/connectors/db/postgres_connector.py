"""Postgres connector using SQLAlchemy engine for chunked exports/imports."""
from __future__ import annotations

from typing import Generator, Iterable, List
from sqlalchemy import create_engine, text, Table, MetaData
from sqlalchemy.sql import insert as sql_insert


class PostgresConnector:
    def __init__(self, url: str):
        self.engine = create_engine(url, future=True)

    def stream_query(self, sql: str, params: dict | None = None, chunk_size: int = 1000) -> Generator[dict, None, None]:
        with self.engine.connect() as conn:
            result = conn.execution_options(stream_results=True).execute(text(sql), params or {})
            for row in result:
                yield dict(row._mapping)

    def write_table(self, table_name: str, rows: Iterable[dict], batch_size: int = 1000):
        """Write rows to a target table in batches using SQLAlchemy core inserts.

        This performs batched `INSERT` operations. For very large imports or
        maximal throughput prefer `COPY`/`COPY FROM STDIN` implementations.
        """
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)

        batch: List[dict] = []
        with self.engine.begin() as conn:
            for row in rows:
                batch.append(row)
                if len(batch) >= batch_size:
                    conn.execute(sql_insert(table), batch)
                    batch.clear()

            if batch:
                conn.execute(sql_insert(table), batch)
