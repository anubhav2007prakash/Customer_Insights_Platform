"""Simple permission code validator."""
import re

PERMISSION_RE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)*$", re.I)


def validate_permission_code(code: str) -> bool:
    return bool(PERMISSION_RE.match(code))
