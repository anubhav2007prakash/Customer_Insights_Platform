"""Basic data cleaning utilities."""
from __future__ import annotations

from typing import Dict, Iterable

from dateutil import parser as date_parser


def trim_spaces(row: Dict[str, any]) -> Dict[str, any]:
    return {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}


def normalize_case(row: Dict[str, any], to_lower: bool = True) -> Dict[str, any]:
    if to_lower:
        return {k: (v.lower() if isinstance(v, str) else v) for k, v in row.items()}
    return {k: (v.upper() if isinstance(v, str) else v) for k, v in row.items()}


def standardize_dates(row: Dict[str, any], date_fields: Iterable[str]) -> Dict[str, any]:
    for f in date_fields:
        if f in row and row[f]:
            try:
                row[f] = date_parser.parse(str(row[f])).isoformat()
            except Exception:
                # leave as-is; validation will flag
                pass
    return row


def normalize_phone(phone: str) -> str:
    if not phone:
        return phone
    digits = "".join([c for c in str(phone) if c.isdigit() or c == "+"])
    return digits


def remove_duplicates(rows: Iterable[Dict[str, any]], key_fields: Iterable[str]):
    seen = set()
    for row in rows:
        key = tuple(row.get(k) for k in key_fields)
        if key in seen:
            continue
        seen.add(key)
        yield row
