from __future__ import annotations

from pathlib import Path

from utils.file_uploads import save_uploaded_files


class DummyUploadedFile:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data

    def read(self, size: int = -1) -> bytes:
        if size == -1:
            return self._data
        return self._data[:size]


def test_save_uploaded_files_saves_pdf_and_excel(tmp_path: Path) -> None:
    uploaded_files = [
        DummyUploadedFile("customer-data.pdf", b"pdf-bytes"),
        DummyUploadedFile("sales.xlsx", b"excel-bytes"),
    ]

    saved_paths = save_uploaded_files(uploaded_files, target_dir=tmp_path)

    assert len(saved_paths) == 2
    assert all(path.exists() for path in saved_paths)
    assert any(path.suffix == ".pdf" for path in saved_paths)
    assert any(path.suffix == ".xlsx" for path in saved_paths)
