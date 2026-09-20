"""Profiling engine for imported datasets."""
from __future__ import annotations

import pandas as pd
from typing import Iterable


class DataProfiler:
    def profile(self, rows: Iterable[dict]) -> dict:
        df = pd.DataFrame(rows)
        total_rows = int(df.shape[0])
        total_columns = int(df.shape[1])

        data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
        null_counts = df.isna().sum().to_dict()
        null_percentage = {col: float((count / total_rows) * 100) if total_rows else 0.0 for col, count in null_counts.items()}
        duplicate_percentage = float((df.duplicated().sum() / total_rows) * 100) if total_rows else 0.0
        unique_values = {col: int(df[col].nunique(dropna=False)) for col in df.columns}
        cardinality = {col: float(df[col].nunique(dropna=True)) for col in df.columns}

        statistics = {}
        for col in df.columns:
            series = df[col].dropna()
            if series.empty:
                statistics[col] = {}
                continue
            try:
                statistics[col] = {
                    "min": series.min() if not series.empty else None,
                    "max": series.max() if not series.empty else None,
                    "mean": float(series.mean()) if series.dtype.kind in "bifc" else None,
                    "median": float(series.median()) if series.dtype.kind in "bifc" else None,
                    "std": float(series.std()) if series.dtype.kind in "bifc" else None,
                    "top_frequencies": series.value_counts(dropna=False).head(10).to_dict(),
                    "empty": int(series.eq("").sum()) if series.dtype == object else 0,
                    "constant": bool(series.nunique(dropna=True) <= 1),
                }
            except Exception:
                statistics[col] = {}

        profile = {
            "total_rows": total_rows,
            "total_columns": total_columns,
            "data_types": data_types,
            "null_counts": null_counts,
            "null_percentage": null_percentage,
            "duplicate_percentage": duplicate_percentage,
            "unique_values": unique_values,
            "cardinality": cardinality,
            "statistics": statistics,
        }

        return profile
