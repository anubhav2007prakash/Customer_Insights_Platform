"""Tenant & Lease Directory — OmniMall AI."""

from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from components.ui.cards import empty_state, progress_bar, section_header, status_indicator
from utils.file_uploads import save_uploaded_files
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page


def init_tenant_state():
    """Initialize mock tenant database in session state."""
    if "tenant_db" not in st.session_state:
        st.session_state["tenant_db"] = pd.DataFrame({
            "Tenant ID": ["TEN-ZARA-01", "TEN-APPL-02", "TEN-PNDA-03", "TEN-SPHR-04", "TEN-AMCT-05", "TEN-STRB-06", "TEN-HNM-07"],
            "Tenant Name": ["Zara", "Apple Store", "Panda Express", "Sephora", "AMC Theatres", "Starbucks", "H&M"],
            "Category": ["Apparel", "Electronics", "Food Court", "Beauty", "Entertainment", "Food & Bev", "Apparel"],
            "Zone": ["South Wing", "North Wing", "Food Court", "East Wing", "Atrium", "North Wing", "South Wing"],
            "Sq Ft": [12500, 8400, 1200, 3200, 45000, 1500, 11000],
            "Monthly Rent": [45000, 32000, 8000, 12000, 110000, 6500, 38000],
            "Lease Expiry": [(datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d") for d in [365, 850, 45, 120, 1400, 60, 210]],
            "Status": ["Active", "Active", "Expiring Soon", "Active", "Active", "Active", "Active"],
        })


def render_upload_tab() -> None:
    """Render the file upload and target import configuration form."""
    section_header("Upload Tenant Data")
    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    st.markdown("Supported formats: PDF, Excel (.xlsx/.xls), CSV, JSON, and Parquet.")

    with st.form("upload_data_form"):
        uploaded = st.file_uploader(
            "Drag & drop or browse files",
            type=["pdf", "xlsx", "xls", "csv", "json", "parquet"],
            accept_multiple_files=True,
            key="tenant_manager_uploader",
        )
        c1, c2 = st.columns(2)
        with c1:
            schema = st.selectbox("Target schema", ["Tenant Directory", "Sales Reports", "Maintenance Logs"])
        with c2:
            mode = st.selectbox("Import mode", ["Append", "Replace", "Merge"])

        submitted = st.form_submit_button("Start Import", type="primary", use_container_width=True)
        if submitted:
            if uploaded:
                try:
                    # Load the first file for dynamic mapping
                    first_file = uploaded[0]
                    if first_file.name.endswith(".csv"):
                        df = pd.read_csv(first_file)
                    elif first_file.name.endswith((".xls", ".xlsx")):
                        df = pd.read_excel(first_file)
                    elif first_file.name.endswith(".json"):
                        df = pd.read_json(first_file)
                    elif first_file.name.endswith(".parquet"):
                        df = pd.read_parquet(first_file)
                    else:
                        st.error("Unsupported file type for dynamic mapping.")
                        return
                    
                    st.session_state["dynamic_dataset"] = df
                    saved_paths = save_uploaded_files(uploaded)
                    st.success(f"Uploaded {len(saved_paths)} file(s). Dataset loaded for dynamic mapping.")
                    for path in saved_paths:
                        st.caption(f"Stored: {path.name}")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
            else:
                st.error("Please select one or more files to upload before starting import.")
    st.markdown("</div>", unsafe_allow_html=True)


def color_status(val):
    if val == "Expiring Soon":
        return 'color: #f59e0b; font-weight: bold;'
    elif val == "Overdue":
        return 'color: #ef4444; font-weight: bold;'
    return 'color: #10b981;'


def render_tenant_tab() -> None:
    """Render physical mall tenant list with search and filter."""
    section_header("Tenant Directory", "Search and manage mall tenants and leases")
    
    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    
    # Filter Controls
    c1, c2 = st.columns([2, 1])
    with c1:
        search_query = st.text_input("Search Tenant Name or ID", placeholder="e.g. Zara or TEN-ZARA...")
    with c2:
        categories = ["All"] + list(st.session_state["tenant_db"]["Category"].unique())
        cat_filter = st.selectbox("Filter by Category", categories)
        
    df = st.session_state["tenant_db"].copy()
    
    # Apply search filter
    if search_query:
        search_query = search_query.lower()
        df = df[df["Tenant ID"].str.lower().str.contains(search_query) | df["Tenant Name"].str.lower().str.contains(search_query)]
        
    # Apply category filter
    if cat_filter != "All":
        df = df[df["Category"] == cat_filter]
        
    # Display styled dataframe
    st.dataframe(
        df.style.map(color_status, subset=['Status']),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Monthly Rent": st.column_config.NumberColumn(format="$%d"),
            "Sq Ft": st.column_config.NumberColumn("Sq Ft", format="%d"),
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    col_add, col_edit = st.columns(2)
    with col_add:
        with st.expander("➕ Add New Tenant"):
            with st.form("add_tenant_form"):
                new_id = st.text_input("Tenant ID", "TEN-NEW-01")
                new_name = st.text_input("Tenant Name")
                col_c, col_s = st.columns(2)
                new_cat = col_c.selectbox("Category", ["Apparel", "Electronics", "Food & Bev", "Beauty", "Entertainment", "Services", "Kiosk"])
                new_zone = col_s.selectbox("Zone", ["North Wing", "South Wing", "East Wing", "Food Court", "Atrium", "Parking Kiosk"])
                
                col_rent, col_sqft = st.columns(2)
                new_rent = col_rent.number_input("Monthly Rent ($)", min_value=0, value=5000)
                new_sqft = col_sqft.number_input("Square Footage", min_value=0, value=1000)
                
                new_expiry = st.date_input("Lease Expiry", datetime.now() + timedelta(days=365))
                
                if st.form_submit_button("Add Tenant", type="primary"):
                    new_row = pd.DataFrame([{
                        "Tenant ID": new_id, "Tenant Name": new_name, "Category": new_cat, "Zone": new_zone,
                        "Sq Ft": new_sqft, "Monthly Rent": new_rent, "Lease Expiry": new_expiry.strftime("%Y-%m-%d"), "Status": "Active"
                    }])
                    st.session_state["tenant_db"] = pd.concat([st.session_state["tenant_db"], new_row], ignore_index=True)
                    st.success(f"Added {new_name} to the directory!")
                    st.rerun()
                    
    with col_edit:
        with st.expander("✏️ Update Lease Status"):
            with st.form("edit_lease_form"):
                tenant_to_edit = st.selectbox("Select Tenant", st.session_state["tenant_db"]["Tenant Name"].tolist())
                new_status = st.selectbox("Status", ["Active", "Expiring Soon", "Renewed", "Terminated"])
                
                if st.form_submit_button("Update Lease"):
                    idx = st.session_state["tenant_db"].index[st.session_state["tenant_db"]["Tenant Name"] == tenant_to_edit].tolist()[0]
                    st.session_state["tenant_db"].at[idx, "Status"] = new_status
                    st.success(f"Updated {tenant_to_edit} lease status to {new_status}.")
                    st.rerun()


def render_pipelines_tab() -> None:
    """Render status of active tenant integrations."""
    section_header("Tenant Integrations & Data Feeds")
    pipelines = [
        ("Anchor Store POS Aggregation", 100, "online"),
        ("Food Court Delivery Apps Sync", 100, "online"),
        ("Parking Garage Payment API", 45, "pending"),
        ("Mall Wi-Fi Analytics Feed", 92, "online"),
    ]
    for name, pct, status in pipelines:
        st.markdown(f"**{name}**")
        status_indicator("Connected" if status == "online" else "Syncing", status)
        progress_bar(pct, f"{pct}% sync progress")
        st.markdown("---")


def render_quality_tab() -> None:
    """Render data quality scores."""
    section_header("Data Quality Score")
    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    progress_bar(96, "Overall Quality: 96%")
    st.markdown("**Issues detected:** 2 missing tax IDs, 0 duplicate records, 0 schema violations")
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Bootstrap and render Data Manager page."""
    init_tenant_state()
    
    bootstrap_page(
        "Tenant Directory",
        "data_manager",
        breadcrumbs=["Mall", "Tenant Directory"],
        subtitle="Manage tenant leases, categories, square footage, and rent",
        icon="🏢",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    section_header("Mall Directory System")

    tab1, tab2, tab3 = st.tabs(["Tenant Directory", "Integrations", "Data Quality"])

    with tab1:
        render_tenant_tab()
    with tab2:
        render_pipelines_tab()
    with tab3:
        render_quality_tab()

    finish_page()


main()
