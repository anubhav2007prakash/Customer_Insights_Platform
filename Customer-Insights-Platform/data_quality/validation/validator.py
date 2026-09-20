"""Schema validation engine for imported datasets."""
from __future__ import annotations

from typing import Iterable
import json
import pandas as pd

from data_quality.exceptions.errors import SchemaValidationError


class SchemaValidator:
    def validate(self, rows: Iterable[dict], schema_spec: dict) -> dict:
        df = pd.DataFrame(rows)
        report = {
            "missing_columns": [],
            "additional_columns": [],
            "type_mismatches": [],
            "invalid_formats": [],
            "row_count": int(df.shape[0]),
        }

        expected_columns = list(schema_spec.get("columns", {}).keys())
        actual_columns = list(df.columns)

        report["missing_columns"] = [col for col in expected_columns if col not in actual_columns]
        report["additional_columns"] = [col for col in actual_columns if col not in expected_columns]

        for col, definition in schema_spec.get("columns", {}).items():
            if col not in actual_columns:
                continue
            values = df[col].dropna()
            expected_type = definition.get("detected_type")
            for index, value in values.items():
                if not self._validate_type(value, expected_type):
                    report["type_mismatches"].append({"column": col, "index": int(index), "value": value, "expected": expected_type})
                if expected_type == "email" and not self._is_email(value):
                    report["invalid_formats"].append({"column": col, "index": int(index), "value": value, "format": "email"})
                if expected_type == "phone" and not self._is_phone(value):
                    report["invalid_formats"].append({"column": col, "index": int(index), "value": value, "format": "phone"})

        if report["missing_columns"] or report["type_mismatches"] or report["invalid_formats"]:
            raise SchemaValidationError(report)

        return report

    def _validate_type(self, value: object, expected_type: str) -> bool:
        if expected_type == "integer":
            return self._is_int(value)
        if expected_type in {"float", "decimal"}:
            return self._is_float(value)
        if expected_type == "boolean":
            return self._is_boolean(value)
        if expected_type in {"date", "datetime"}:
            return self._is_datetime(value)
        if expected_type == "uuid":
            return self._is_uuid(value)
        if expected_type == "json":
            return self._is_json(value)
        if expected_type in {"email", "phone", "url", "currency", "text", "category"}:
            return True
        return False

    def _is_int(self, value: object) -> bool:
        try:
            int(value)
            return True
        except Exception:
            return False

    def _is_float(self, value: object) -> bool:
        try:
            float(value)
            return True
        except Exception:
            return False

    def _is_boolean(self, value: object) -> bool:
        return str(value).strip().lower() in {"true", "false", "yes", "no", "0", "1"}

    def _is_datetime(self, value: object) -> bool:
        try:
            pd.to_datetime(value)
            return True
        except Exception:
            return False

    def _is_uuid(self, value: object) -> bool:
        import re
        pattern = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
        return bool(pattern.match(str(value)))

    def _is_email(self, value: object) -> bool:
        import re
        pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        return bool(pattern.match(str(value)))

    def _is_phone(self, value: object) -> bool:
        import re
        pattern = re.compile(r"^\+?[0-9\-\s]{7,20}$")
        return bool(pattern.match(str(value)))

    def _is_json(self, value: object) -> bool:
        try:
            json.loads(str(value))
            return True
        except Exception:
            return False
