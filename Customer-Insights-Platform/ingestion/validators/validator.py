"""Validation rules and report generation."""
from __future__ import annotations

import re
from typing import Dict, Iterable, List, Tuple

from dateutil import parser as date_parser


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9+()\-\s]{7,20}$")


def validate_row(row: Dict[str, any], required: Iterable[str] = ()) -> Tuple[bool, List[str]]:
    """Validate a single row and return (is_valid, errors)."""
    errors: List[str] = []

    # required fields
    for col in required:
        if col not in row or row.get(col) in (None, ""):
            errors.append(f"Missing required column: {col}")

    # email heuristics
    if "email" in row and row.get("email"):
        if not EMAIL_RE.match(str(row.get("email"))):
            errors.append("Invalid email format")

    # phone heuristics
    if "phone" in row and row.get("phone"):
        if not PHONE_RE.match(str(row.get("phone"))):
            errors.append("Invalid phone format")

    # date heuristics
    for k, v in row.items():
        if k.lower().endswith("date") or k.lower().startswith("date_"):
            if v in (None, ""):
                continue
            try:
                date_parser.parse(str(v))
            except Exception:
                errors.append(f"Invalid date in column {k}: {v}")

    return (len(errors) == 0, errors)


def validate_stream(rows: Iterable[Dict[str, any]], required: Iterable[str] = ()) -> Dict:
    """Validate an iterable of rows and return a detailed report."""
    total = 0
    passed = 0
    failed = 0
    error_rows: List[Dict] = []

    for i, row in enumerate(rows):
        total += 1
        ok, errors = validate_row(row, required=required)
        if ok:
            passed += 1
        else:
            failed += 1
            error_rows.append({"row_index": i, "errors": errors, "row": row})

    return {"total": total, "passed": passed, "failed": failed, "errors": error_rows}
