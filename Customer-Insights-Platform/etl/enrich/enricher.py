"""Enrichment utilities for customer records."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List


def calculate_age(birth_date_str: str) -> int | None:
    try:
        dt = datetime.fromisoformat(birth_date_str)
        today = datetime.utcnow()
        return today.year - dt.year - ((today.month, today.day) < (dt.month, dt.day))
    except Exception:
        return None


def enrich_record(r: Dict) -> Dict:
    out = dict(r)
    # full name
    if not out.get("full_name"):
        parts = [out.get("first_name"), out.get("last_name")]
        out["full_name"] = " ".join([p for p in parts if p])

    # age
    bd = out.get("birth_date")
    if bd:
        out["age"] = calculate_age(bd)

    # customer hash id (stable)
    import hashlib

    key = (out.get("email") or "") + "|" + (str(out.get("customer_id")) or "")
    out["customer_hash"] = hashlib.sha256(key.encode("utf-8")).hexdigest()

    return out


def enrich_batch(rows: Iterable[Dict]) -> List[Dict]:
    return [enrich_record(r) for r in rows]
