"""Data Import & Ingestion — OmniMall AI."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from components.ui.cards import section_header
from utils.file_uploads import save_uploaded_files
from utils.page_bootstrap import bootstrap_page, finish_page


def render_pipeline_status_board() -> None:
    """Render #18 Data Pipeline Status Board."""
    section_header("⚙️ Data Pipeline Status Board", "Real-time automated ingestion pipeline monitoring")

    pipelines = [
        {"name": "Footfall Sensors (IoT Gateways)", "source": "MQTT / Kafka", "status": "running", "progress": 100, "latency": "1.2s", "rows": "1.4M/day"},
        {"name": "Tenant POS Sales Sync", "source": "Rest API (Webhooks)", "status": "running", "progress": 100, "latency": "450ms", "rows": "84K/day"},
        {"name": "Parking Barrier Cameras (ANPR)", "source": "RTSP Stream", "status": "running", "progress": 100, "latency": "800ms", "rows": "24K/day"},
        {"name": "Loyalty App Member Activity", "source": "PostgreSQL Replica", "status": "pending", "progress": 45, "latency": "15s", "rows": "12K/day"},
        {"name": "HVAC Telemetry & Weather", "source": "BACnet / NOAA API", "status": "idle", "progress": 0, "latency": "5m", "rows": "1.2K/day"},
    ]

    for p in pipelines:
        st.html(
            f"""
            <div class="if-pipeline-row">
                <div>
                    <div class="if-pipeline-name">{p['name']}</div>
                    <div class="if-pipeline-source">Source: {p['source']} · Latency: {p['latency']} · Volume: {p['rows']}</div>
                </div>
                <span class="if-pipeline-status {p['status']}">{p['status'].upper()}</span>
                <div class="if-pipeline-progress">
                    <div class="if-pipeline-progress-fill" style="width:{p['progress']}%;"></div>
                </div>
            </div>
            """
        )


def main() -> None:
    """Bootstrap and render the Data Ingestion page."""
    bootstrap_page(
        "Data Import",
        "data_import",
        breadcrumbs=["Mall Overview", "Data Import"],
        subtitle="Upload tenant feeds, footfall sensor logs, or any dataset to instantly power all charts and AI models",
        icon="📤",
    )

    tab1, tab2 = st.tabs(["📤 File Import", "⚙️ Pipeline Board"])

    with tab1:
        section_header("Upload Tenant Feeds & Footfall Sensor Data")

        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        st.markdown("**Supported formats:** Excel (.xlsx/.xls), CSV, JSON, and Parquet.")
        st.markdown(
            "Once uploaded, all charts on the Dashboard, Traffic Analytics, Forecasting, and AI pages will "
            "**dynamically re-render** based on your dataset — from revenue trends to footfall heatmaps."
        )

        st.info(
            "💡 **Tip:** Your dataset can include any columns — the platform's AI engine automatically detects "
            "date columns, revenue/sales amounts, footfall counts, tenant categories, and zone information.",
            icon="ℹ️",
        )

        with st.form("upload_data_form"):
            uploaded = st.file_uploader(
                "Drag & drop or browse files",
                type=["xlsx", "xls", "csv", "json", "parquet"],
                accept_multiple_files=False,
                key="data_ingestion_uploader",
            )

            c1, c2 = st.columns(2)
            with c1:
                schema = st.selectbox(
                    "Data Type",
                    [
                        "Footfall Sensor Logs",
                        "Tenant POS / Sales Data",
                        "Lease & Occupancy Records",
                        "Mall Event Registrations",
                        "Loyalty Member Data",
                        "Parking Utilization Logs",
                        "Custom / Other",
                    ]
                )
            with c2:
                mode = st.selectbox("Import Mode", ["Replace current dataset", "Append to existing"])

            submitted = st.form_submit_button("Start Import & Refresh Engine", type="primary", use_container_width=True)
            if submitted:
                if uploaded:
                    try:
                        if uploaded.name.endswith(".csv"):
                            df = pd.read_csv(uploaded)
                        elif uploaded.name.endswith((".xls", ".xlsx")):
                            df = pd.read_excel(uploaded)
                        elif uploaded.name.endswith(".json"):
                            df = pd.read_json(uploaded)
                        elif uploaded.name.endswith(".parquet"):
                            df = pd.read_parquet(uploaded)
                        else:
                            st.error("Unsupported file type for dynamic mapping.")
                            st.stop()

                        st.session_state["dynamic_dataset"] = df
                        save_uploaded_files([uploaded])

                        st.success(
                            f"✅ **{schema}** dataset loaded successfully! All charts and AI models are now dynamically "
                            f"mapped to your data (`{len(df):,}` rows × `{len(df.columns)}` columns)."
                        )
                        st.caption(f"File: {uploaded.name} | Rows: {len(df):,} | Columns: {len(df.columns)}")

                        with st.expander("🔍 Preview Dataset"):
                            st.dataframe(df.head(10), use_container_width=True)

                    except Exception as e:
                        st.error(f"Error reading file: {e}")
                else:
                    st.error("Please select a file to upload before starting import.")

        st.markdown("</div>", unsafe_allow_html=True)

        if "dynamic_dataset" in st.session_state and st.session_state["dynamic_dataset"] is not None:
            st.divider()
            section_header("Active Dataset Schema", "Column mapping detected by the AI engine")
            df = st.session_state["dynamic_dataset"]
            cols_df = pd.DataFrame({
                "Column Name": df.columns,
                "Data Type": df.dtypes.astype(str),
                "Non-Null Count": df.count().values,
                "Sample Value": [str(df[c].dropna().iloc[0]) if not df[c].dropna().empty else "N/A" for c in df.columns],
            })
            st.dataframe(cols_df, hide_index=True, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Dataset", type="secondary", use_container_width=True):
                    del st.session_state["dynamic_dataset"]
                    st.success("Dataset cleared. Default demo data will be used.")
                    st.rerun()
            with col2:
                if st.button("🔄 Refresh All Charts", type="primary", use_container_width=True):
                    st.success("Charts refreshed with the current dataset.")
                    st.rerun()

    with tab2:
        render_pipeline_status_board()

    finish_page()


main()
