"""Helpers for uploading customer files through the Streamlit UI."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, List, Sequence


DEFAULT_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"


def save_uploaded_files(uploaded_files: Sequence[object] | Iterable[object], target_dir: str | Path | None = None) -> List[Path]:
    """Persist uploaded files to disk and return the saved paths."""

    destination_dir = Path(target_dir) if target_dir is not None else DEFAULT_UPLOAD_DIR
    destination_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: List[Path] = []
    for uploaded_file in uploaded_files:
        if not hasattr(uploaded_file, "name") or not hasattr(uploaded_file, "read"):
            continue

        filename = Path(uploaded_file.name).name
        destination_path = destination_dir / filename

        data = uploaded_file.read()
        if hasattr(data, "decode"):
            data = data.decode("utf-8", errors="ignore")
        if isinstance(data, str):
            destination_path.write_text(data, encoding="utf-8")
        else:
            destination_path.write_bytes(data)

        saved_paths.append(destination_path)
    return saved_paths
