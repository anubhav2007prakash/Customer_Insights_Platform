"""CSV parser with streaming support and delimiter detection."""
from __future__ import annotations

import csv
from typing import Dict, Generator, IO, Optional


def parse_csv(fileobj: IO[str], delimiter: Optional[str] = None, encoding: str = "utf-8") -> Generator[Dict[str, str], None, None]:
    """Yield rows as dictionaries from a CSV file-like object.

    - Detects delimiter if not provided.
    - Handles missing headers by creating generic column names.
    - Streams rows to avoid large memory usage.
    """
    # If fileobj is a binary stream, decode externally; assume text IO here.
    sample = fileobj.read(8192)
    fileobj.seek(0)

    if not delimiter:
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            delimiter = dialect.delimiter
        except Exception:
            delimiter = ","

    reader = csv.reader(fileobj, delimiter=delimiter)
    try:
        headers = next(reader)
    except StopIteration:
        return

    # normalize headers
    headers = [h.strip() if h and h.strip() != "" else f"column_{i}" for i, h in enumerate(headers)]

    for row in reader:
        # pad or trim to headers
        if len(row) < len(headers):
            row = row + [None] * (len(headers) - len(row))
        yield {headers[i]: (row[i].strip() if isinstance(row[i], str) else row[i]) for i in range(len(headers))}
