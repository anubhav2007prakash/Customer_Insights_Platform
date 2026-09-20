"""Configurable transformation engine for ETL pipelines."""
from __future__ import annotations

from typing import Callable, Dict, Iterable, List
from dateutil import parser as date_parser
import requests
from decimal import Decimal


class TransformationError(Exception):
    pass


class Transformer:
    """Apply a sequence of configurable column-level transformations.

    Config example:
    [
      {"action": "rename", "from": "fname", "to": "first_name"},
      {"action": "drop", "cols": ["tmp"]},
      {"action": "merge", "into": "full_name", "cols": ["first_name","last_name"], "sep": " "},
      {"action": "format_date", "col": "birth_date", "fmt": "%Y-%m-%d"}
    ]
    """

    def __init__(self, spec: List[dict], custom_fns: Dict[str, Callable] | None = None, currency_provider: Callable[[str, str], Decimal] | None = None):
        self.spec = spec or []
        self.custom_fns = custom_fns or {}
        # currency_provider(from_code, to_code) -> Decimal multiplier
        self.currency_provider = currency_provider

    def apply(self, row: dict) -> dict:
        r = dict(row)
        for step in self.spec:
            action = step.get("action")
            if action == "rename":
                frm = step.get("from")
                to = step.get("to")
                if frm in r:
                    r[to] = r.pop(frm)
            elif action == "drop":
                for c in step.get("cols", []):
                    r.pop(c, None)
            elif action == "merge":
                cols = step.get("cols", [])
                sep = step.get("sep", " ")
                vals = [str(r.get(c, "")) for c in cols]
                r[step.get("into")] = sep.join([v for v in vals if v])
            elif action == "split":
                col = step.get("col")
                into = step.get("into", [])
                sep = step.get("sep", " ")
                parts = str(r.get(col, "")).split(sep)
                for i, c in enumerate(into):
                    r[c] = parts[i] if i < len(parts) else None
            elif action == "format_date":
                col = step.get("col")
                fmt = step.get("fmt")
                val = r.get(col)
                if val:
                    try:
                        dt = date_parser.parse(val)
                        r[col] = dt.strftime(fmt)
                    except Exception as exc:
                        raise TransformationError(f"format_date failed for {col}: {exc}")
            elif action == "convert_bool":
                col = step.get("col")
                v = r.get(col)
                if isinstance(v, str):
                    r[col] = v.strip().lower() in ("true", "1", "yes", "y")
                else:
                    r[col] = bool(v)
            elif action == "default":
                col = step.get("col")
                if r.get(col) in (None, ""):
                    r[col] = step.get("value")
            elif action == "custom":
                name = step.get("fn")
                fn = self.custom_fns.get(name)
                if not fn:
                    raise TransformationError(f"custom function {name} not found")
                r = fn(r)
            elif action == "currency_convert":
                col = step.get("col")
                to = step.get("to_currency")
                val = r.get(col)
                if val is not None:
                    try:
                        amount = Decimal(str(val))
                        from_cur = step.get("from_currency") or (step.get("currency_col") and r.get(step.get("currency_col")))
                        if not from_cur:
                            raise TransformationError("currency source not specified")
                        rate = None
                        if self.currency_provider:
                            rate = self.currency_provider(from_cur, to)
                        else:
                            res = requests.get(f"https://api.exchangerate.host/convert?from={from_cur}&to={to}")
                            rate = Decimal(str(res.json().get("info", {}).get("rate", 1)))
                        r[col] = float((amount * rate).quantize(Decimal("0.01")))
                    except Exception as exc:
                        raise TransformationError(f"currency_convert failed for {col}: {exc}")
            else:
                # unknown actions are ignored for forward-compat
                continue

        return r
