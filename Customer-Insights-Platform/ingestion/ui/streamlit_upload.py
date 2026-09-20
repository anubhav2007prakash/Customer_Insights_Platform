"""Streamlit upload UI for ingestion with drag-and-drop, progress, previews."""
from __future__ import annotations

import streamlit as st
from ingestion.services.ingestion_service import IngestionService


def app():
    st.title("Upload Data - InsightForge Ingestion")
    uploaded = st.file_uploader("Drop files here or click to browse", accept_multiple_files=True)
    svc = IngestionService()

    for file in uploaded or []:
        st.write(f"Previewing: {file.name}")
        data = file.read()
        try:
            preview = svc.preview(data, file.name)
            st.write(preview.preview)
        except Exception as exc:
            st.error(f"Failed preview: {exc}")

        if st.button(f"Import {file.name}"):
            with st.spinner("Importing..."):
                report = svc.import_file(organization_id=st.session_state.get("organization_id"), user_id=st.session_state.get("user_id", "ui"), file_bytes=data, filename=file.name, required=["email"])
                st.success(f"Import complete: {report.passed}/{report.total} passed")

if __name__ == "__main__":
    app()
