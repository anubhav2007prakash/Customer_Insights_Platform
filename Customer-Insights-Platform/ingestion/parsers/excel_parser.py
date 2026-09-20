"""Excel parser using openpyxl (if available).

Falls back with a helpful error message if dependency missing.
"""
from __future__ import annotations

from typing import Dict, Generator, IO


def parse_excel(fileobj: IO[bytes], sheet: int = 0) -> Generator[Dict[str, str], None, None]:
    try:
        import openpyxl
    except Exception as exc:  # pragma: no cover - external dependency
        raise ImportError("openpyxl is required to parse Excel files. Add it to requirements.txt") from exc

    wb = openpyxl.load_workbook(fileobj, read_only=True, data_only=True)
    sheets = wb.worksheets
    ws = sheets[sheet]

    rows = ws.iter_rows(values_only=True)
    try:
        headers = next(rows)
    except StopIteration:
        return

    headers = [h.strip() if h and isinstance(h, str) and h.strip() != "" else f"column_{i}" for i, h in enumerate(headers)]

    for r in rows:
        yield {headers[i]: (r[i] if r[i] is not None else None) for i in range(len(headers))}
