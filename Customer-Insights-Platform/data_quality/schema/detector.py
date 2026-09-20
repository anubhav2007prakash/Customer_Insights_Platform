"""Detect dataset schema and infer data types."""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Iterable

import pandas as pd


class SchemaDetector:
    TYPE_MAP = {
        "integer": int,
        "float": float,
        "decimal": float,
        "boolean": bool,
        "date": "date",
        "datetime": "datetime",
        "email": "email",
        "phone": "phone",
        "url": "url",
        "uuid": "uuid",
        "currency": "currency",
        "json": "json",
        "text": str,
        "category": "category",
    }

    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    PHONE_RE = re.compile(r"^\+?[0-9\-\s]{7,20}$")
    URL_RE = re.compile(r"^(https?://).+")
    UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")

    def detect(self, rows: Iterable[dict], overrides: dict | None = None) -> dict:
        df = pd.DataFrame(rows)
        schema = {}
        overrides = overrides or {}

        for col in df.columns:
            if col in overrides:
                schema[col] = overrides[col]
                continue

            series = df[col].dropna()
            inferred_type = self._infer_type(series)
            schema[col] = {
                "detected_type": inferred_type,
                "nullable": bool(df[col].isna().any()),
                "unique": int(df[col].nunique(dropna=False) == df.shape[0]) if df.shape[0] else False,
            }

        return {"columns": schema, "detected_at": datetime.utcnow().isoformat()}

    def _infer_type(self, series: pd.Series) -> str:
        if series.empty:
            return "text"

        if self._all_match(series, self.UUID_RE):
            return "uuid"
        if self._all_match(series, self.EMAIL_RE):
            return "email"
        if self._all_match(series, self.PHONE_RE):
            return "phone"
        if self._all_match(series, self.URL_RE):
            return "url"
        if self._all_dates(series):
            return "datetime"
        if self._all_integer(series):
            return "integer"
        if self._all_float(series):
            return "float"
        if self._all_json(series):
            return "json"
        if self._all_boolean(series):
            return "boolean"
        if self._all_currency(series):
            return "currency"

        distinct_ratio = series.nunique(dropna=True) / len(series)
        if distinct_ratio < 0.2 and len(series) > 10:
            return "category"

        return "text"

    def _all_match(self, series: pd.Series, pattern: re.Pattern) -> bool:
        return series.apply(lambda v: bool(pattern.match(str(v)))).all()

    def _all_dates(self, series: pd.Series) -> bool:
        try:
            pd.to_datetime(series, errors="raise")
            return True
        except Exception:
            return False

    def _all_integer(self, series: pd.Series) -> bool:
        return pd.api.types.is_integer_dtype(series) or series.apply(lambda v: str(v).isdigit()).all()

    def _all_float(self, series: pd.Series) -> bool:
        try:
            series.astype(float)
            return True
        except Exception:
            return False

    def _all_json(self, series: pd.Series) -> bool:
        try:
            series.apply(lambda v: json.loads(str(v)))
            return True
        except Exception:
            return False

    def _all_boolean(self, series: pd.Series) -> bool:
        return series.apply(lambda v: str(v).strip().lower() in {"true", "false", "yes", "no", "0", "1"}).all()

    def _all_currency(self, series: pd.Series) -> bool:
        return series.apply(lambda v: str(v).strip().replace("$", "").replace(",", "").replace(".", "", 1).isdigit()).all()
