"""Unit tests for validation and cleaning."""
from __future__ import annotations

from ingestion.validators.validator import validate_row, validate_stream
from ingestion.cleaners.cleaner import trim_spaces, normalize_case, standardize_dates


def test_validate_row_email_and_date():
    row = {"email": "bad-email", "signup_date": "2020-13-01"}
    ok, errors = validate_row(row, required=["email"])  # type: ignore
    assert not ok
    assert any("Invalid email" in e or "Invalid date" in e for e in errors)


def test_cleaning_trim_and_date():
    row = {"name": " Alice ", "signup_date": "2020-01-02"}
    r = trim_spaces(row)
    assert r["name"] == "Alice"
    r2 = standardize_dates(r, ["signup_date"])
    assert r2["signup_date"].startswith("2020-01-02")
