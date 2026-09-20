"""Unit tests for parsers."""
from __future__ import annotations

import io
from ingestion.parsers.csv_parser import parse_csv
from ingestion.parsers.json_parser import parse_json


def test_csv_parse_basic():
    s = """name,age,email\nAlice,30,alice@example.com\nBob,25,bob@example.com\n"""
    f = io.StringIO(s)
    rows = list(parse_csv(f))
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice"


def test_json_parse_array_and_ndjson():
    arr = '[{"name": "A"}, {"name": "B"}]'
    f = io.StringIO(arr)
    rows = list(parse_json(f))
    assert len(rows) == 2

    nd = '{"name":"X"}\n{"name":"Y"}\n'
    f2 = io.StringIO(nd)
    rows2 = list(parse_json(f2))
    assert len(rows2) == 2
