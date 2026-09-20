"""Column mapping utilities.

Supports auto-mapping via exact or case-insensitive matches and manual mapping templates.
"""
from __future__ import annotations

from typing import Dict, Iterable, Tuple


def auto_map_columns(source_columns: Iterable[str], target_fields: Iterable[str]) -> Dict[str, str]:
    """Return a mapping from target_field -> source_column using heuristics."""
    src = list(source_columns)
    tgt = list(target_fields)
    mapping: Dict[str, str] = {}

    lower_src = {s.lower(): s for s in src}

    for t in tgt:
        t_low = t.lower()
        if t_low in lower_src:
            mapping[t] = lower_src[t_low]
        else:
            # try substrings
            found = None
            for s in src:
                if t_low in s.lower() or s.lower() in t_low:
                    found = s
                    break
            if found:
                mapping[t] = found

    return mapping


def apply_mapping(row: Dict[str, any], mapping: Dict[str, str]) -> Dict[str, any]:
    """Apply mapping to a single row producing target-keyed dict."""
    out: Dict[str, any] = {}
    for target, source in mapping.items():
        out[target] = row.get(source)
    return out
