"""Deduplication utilities supporting multiple strategies."""
from __future__ import annotations

from typing import Iterable, List, Tuple, Dict


def deduplicate(rows: Iterable[dict], keys: List[str], strategy: str = "keep_first") -> Tuple[List[dict], List[dict]]:
    """Return (deduped_rows, duplicates).

    Strategies: keep_first, keep_latest (requires 'updated_at'), merge (merge non-null), flag
    """
    seen: Dict[tuple, dict] = {}
    duplicates: List[dict] = []

    for r in rows:
        key = tuple(r.get(k) for k in keys)
        if key in seen:
            existing = seen[key]
            if strategy == "keep_first":
                duplicates.append(r)
            elif strategy == "keep_latest":
                # prefer record with later updated_at
                if r.get("updated_at") and existing.get("updated_at"):
                    if r["updated_at"] > existing["updated_at"]:
                        duplicates.append(existing)
                        seen[key] = r
                    else:
                        duplicates.append(r)
                else:
                    duplicates.append(r)
            elif strategy == "merge":
                merged = dict(existing)
                for k, v in r.items():
                    if merged.get(k) in (None, "") and v not in (None, ""):
                        merged[k] = v
                seen[key] = merged
            elif strategy == "flag":
                # keep both but mark
                r["_duplicate_flag"] = True
                existing["_duplicate_flag"] = True
                duplicates.append(r)
            else:
                duplicates.append(r)
        else:
            seen[key] = r

    return list(seen.values()), duplicates
