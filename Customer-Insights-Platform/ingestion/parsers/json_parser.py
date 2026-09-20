"""JSON parsers for arrays and newline-delimited JSON."""
from __future__ import annotations

import json
from typing import Dict, Generator, IO


def parse_json(fileobj: IO[str]) -> Generator[Dict, None, None]:
    """Yield JSON objects from a file. Supports NDJSON and JSON arrays."""
    # Read small sample to decide
    pos = fileobj.tell()
    sample = fileobj.read(4096).lstrip()
    fileobj.seek(pos)

    if not sample:
        return

    if sample.startswith("["):
        data = json.load(fileobj)
        for item in data:
            yield item
    else:
        # NDJSON
        for line in fileobj:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)
