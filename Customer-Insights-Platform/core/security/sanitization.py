"""Input sanitization utilities."""

from __future__ import annotations

import html
import re
from pathlib import Path

from core.exceptions.base import FileValidationError

_UNSAFE_FILENAME = re.compile(r"[^\w\s.-]", re.UNICODE)
_MAX_STRING_LENGTH = 10_000


def sanitize_string(value: str, *, max_length: int = _MAX_STRING_LENGTH) -> str:
    """Strip, truncate, and HTML-escape user input."""
    cleaned = html.escape(value.strip())
    return cleaned[:max_length]


def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded file names to prevent path traversal."""
    name = Path(filename).name
    safe = _UNSAFE_FILENAME.sub("", name).strip()
    if not safe or safe.startswith("."):
        raise FileValidationError(message="Invalid file name.", details={"filename": filename})
    return safe[:255]
