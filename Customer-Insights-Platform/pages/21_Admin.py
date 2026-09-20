"""Facilities & Security Operations — OmniMall AI."""

from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from components.ui.cards import alert_banner, hero_section, metric_grid, section_header, status_indicator
from utils.helpers import get_dashboard_context, relative_time
from utils.page_bootstrap import bootstrap_page, finish_page


def render_roster_tab() -> None:
    """Render the Security & Facilities Staff Roster tab."""
    section_header("Security & Facilities Roster", "Monitor who is on duty across the mall today")

    st.dataframe(
        pd.DataFrame({
            "Staff Member": ["James Okafor", "Linda Torres", "Ravi Sharma", "Maya Chen", "Derek Phillips", "Anita Walsh"],
            "Role": ["Security Chief", "HVAC Technician", "Cleaning Supervisor", "Security Guard", "Electrician", "Security Guard"],
            "Zone": ["All Wings", "Mechanical Room", "Food Court", "North Wing", "East Wing", "South Wing"],
            "Shift": ["08:00 AM – 08:00 PM", "07:00 AM – 03:00 PM", "06:00 AM – 02:00 PM", "12:00 PM – 08:00 PM", "08:00 AM – 05:00 PM", "04:00 PM – 12:00 AM"],
            "Status": ["✅ On Duty", "✅ On Duty", "✅ On Duty", "⏳ Starting Soon", "✅ On Duty", "⏳ Starting Soon"],
        }),
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("➕ Add Staff Shift", expanded=False):
        with st.form("add_shift_form"):
            emp_name = st.text_input("Staff Member Name")
            emp_role = st.selectbox("Role", ["Security Guard", "HVAC Technician", "Cleaning Crew", "Electrician", "Security Chief", "Maintenance Tech"])
            zone = st.selectbox("Assigned Zone", ["All Wings", "North Wing", "South Wing", "East Wing", "Food Court", "Atrium", "Parking Garages", "Mechanical Room"])
            shift_time = st.text_input("Shift Time", placeholder="e.g. 09:00 AM – 05:00 PM")
            submitted = st.form_submit_button("Schedule Shift", type="primary", use_container_width=True)
            if submitted:
                if not emp_name:
                    st.error("Please enter a staff member name.")
                else:
                    st.success(f"Shift scheduled for **{emp_name}** as **{emp_role}** in **{zone}**.")


def render_facilities_tab() -> None:
    """Render the Facilities & HVAC System Status tab."""
    section_header("Facilities & HVAC System Status", "Monitor escalators, elevators, HVAC units, and Wi-Fi")
    flags = [
        ("North Wing Escalators (Up & Down)", True),
        ("South Wing Elevators (Bank 1 & 2)", True),
        ("Food Court HVAC – Zone A", False),
        ("Atrium HVAC – Zone B", True),
        ("Public Wi-Fi (All Wings)", True),
        ("Parking Garage LED Lighting", True),
    ]
    flag_state = {}
    for flag, default in flags:
        key = f"if_facility_{flag.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('&', '')}"
        if key not in st.session_state:
            st.session_state[key] = default
        flag_state[flag] = st.toggle(flag, value=st.session_state[key], key=key)

    if st.button("Save Facility Status", type="primary"):
        for flag, _ in flags:
            key = f"if_facility_{flag.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('&', '')}"
            st.session_state[key] = flag_state.get(flag, False)
        st.success("Facility status updated. Maintenance team has been notified of changes.")


def render_hardware_tab() -> None:
    """Render the Mall Hardware & Systems Status tab."""
    section_header("Mall Systems Status", "Monitor physical mall infrastructure and IoT devices")
    services = [
        ("ShopperTrak Sensors – North Gate", "online"),
        ("ShopperTrak Sensors – South Gate", "online"),
        ("Security Camera Network (248 cameras)", "online"),
        ("POS Aggregation Server", "online"),
        ("Parking Management System", "pending"),
        ("Emergency PA / Fire Alarm System", "online"),
        ("Public Wi-Fi Controller", "online"),
    ]

    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    for svc, status in services:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{svc}**")
        with c2:
            if status == "online":
                status_indicator("Online", "online")
            elif status == "pending":
                status_indicator("Degraded", "pending")
            else:
                status_indicator("Error", "danger")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Run System Health Check", type="primary"):
        st.success("✅ Health check complete. Parking Management System is being rebooted automatically.")


def render_incident_tab() -> None:
    """Render Incident Reports & Security Logs tab."""
    section_header("Security Incident Log", "Review security events, crowd alerts, and maintenance work orders")

    now = datetime.now()
    logs = pd.DataFrame({
        "Timestamp": [
            now - timedelta(minutes=15),
            now - timedelta(minutes=42),
            now - timedelta(hours=2),
            now - timedelta(hours=3, minutes=15),
        ],
        "Reported By": ["James Okafor", "Maya Chen", "System (AI)", "Linda Torres"],
        "Incident": ["Crowd Density Alert – Atrium", "Suspicious Package – South Gate", "HVAC Fault – Food Court Zone A", "Escalator Emergency Stop – North Wing"],
        "Priority": ["⚠️ Medium", "🚨 High", "⚠️ Medium", "⚠️ Medium"],
        "Status": ["Resolved", "Escalated to Police", "Under Repair", "Resolved"],
    })

    logs["Timestamp"] = logs["Timestamp"].apply(relative_time)
    st.dataframe(logs, use_container_width=True, hide_index=True)

    st.divider()
    with st.form("log_incident_form"):
        st.markdown("**Log a New Incident**")
        c1, c2 = st.columns(2)
        with c1:
            inc_type = st.selectbox("Incident Type", ["Crowd Alert", "Suspicious Behaviour", "Slip/Fall", "HVAC Fault", "Electrical Issue", "Fire Alarm", "Theft"])
            inc_zone = st.selectbox("Zone", ["North Wing", "South Wing", "East Wing", "Food Court", "Atrium", "Parking Garage A", "Parking Garage B"])
        with c2:
            inc_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            inc_reporter = st.text_input("Reported By", placeholder="Your name...")
        inc_notes = st.text_area("Notes / Description")
        if st.form_submit_button("Submit Incident Report", type="primary"):
            if inc_reporter:
                st.success(f"✅ **{inc_type}** incident logged in **{inc_zone}** as **{inc_priority}** priority.")
            else:
                st.error("Please enter your name before submitting.")


def main() -> None:
    """Bootstrap and render the Facilities & Security page."""
    bootstrap_page(
        "Facilities & Security",
        "admin",
        breadcrumbs=["Mall Operations", "Facilities & Security"],
        subtitle="Manage security staff rosters, HVAC systems, hardware health, and incident reports",
        icon="🏗️",
    )

    hero_section(
        "Facilities & Security Operations",
        "Keep the mall running safely and smoothly by managing security staff rosters, monitoring HVAC and escalator systems, and logging security incidents in real time.",
        [("View Security Cameras", "video"), ("Log Incident", "alert-triangle")],
    )

    alert_banner("warning", "HVAC Fault – Food Court", "HVAC unit in Food Court Zone A is operating at 40% capacity. Technician dispatched.")

    metric_grid([
        {"label": "Security Staff On Duty", "value": "24", "change": 4.0, "icon": "shield", "tone": "primary"},
        {"label": "Systems Online", "value": "6/7", "change": 0, "icon": "hard-drive", "tone": "warning"},
        {"label": "Incidents Today", "value": "4", "change": -2.0, "icon": "alert-triangle", "tone": "success"},
        {"label": "Mall Open Duration", "value": "6h 42m", "change": 0, "icon": "clock", "tone": "neutral"},
    ], columns=4)

def render_audit_log_tab() -> None:
    """Render interactive system audit log viewer with search and export capabilities."""
    section_header("Audit Log Inspector", "Real-time security, identity, and operational event trail")

    logs_df = pd.DataFrame([
        {"Timestamp": "2026-08-06 18:52:10", "Actor": "alex.morgan@acmecorp.com", "Action": "Exported Executive Summary (PDF)", "Category": "EXPORT", "IP": "192.168.1.42", "Severity": "INFO"},
        {"Timestamp": "2026-08-06 18:44:22", "Actor": "system_auto", "Action": "Triggered automated backup job #8491", "Category": "SYSTEM", "IP": "127.0.0.1", "Severity": "INFO"},
        {"Timestamp": "2026-08-06 18:31:05", "Actor": "linda.torres@omnimall.ai", "Action": "Updated HVAC Unit 2 status to Maintenance", "Category": "UPDATE", "IP": "10.0.4.12", "Severity": "WARN"},
        {"Timestamp": "2026-08-06 18:15:40", "Actor": "james.okafor@omnimall.ai", "Action": "Logged security incident INC-492", "Category": "CREATE", "IP": "10.0.4.15", "Severity": "WARN"},
        {"Timestamp": "2026-08-06 17:50:12", "Actor": "rachel.wong@omnimall.ai", "Action": "Modified tenant lease L003 stage to Renewal", "Category": "UPDATE", "IP": "192.168.1.88", "Severity": "INFO"},
        {"Timestamp": "2026-08-06 17:12:00", "Actor": "alex.morgan@acmecorp.com", "Action": "Generated API Key 'Production-Primary'", "Category": "SECURITY", "IP": "192.168.1.42", "Severity": "WARN"},
        {"Timestamp": "2026-08-06 16:45:18", "Actor": "system_auto", "Action": "Purged transient session cache (142MB)", "Category": "DELETE", "IP": "127.0.0.1", "Severity": "INFO"},
        {"Timestamp": "2026-08-06 15:20:00", "Actor": "failed_login_attempt", "Action": "Failed login attempt from unknown origin", "Category": "SECURITY", "IP": "185.220.101.5", "Severity": "HIGH"},
    ])

    ac1, ac2 = st.columns([2, 1])
    with ac1:
        search_query = st.text_input("🔍 Search Actor / Action / IP", "", key="audit_search")
    with ac2:
        cat_filter = st.selectbox("Category Filter", ["ALL", "SECURITY", "EXPORT", "UPDATE", "CREATE", "DELETE", "SYSTEM"], key="audit_cat")

    filtered_logs = logs_df.copy()
    if cat_filter != "ALL":
        filtered_logs = filtered_logs[filtered_logs["Category"] == cat_filter]
    if search_query:
        filtered_logs = filtered_logs[
            filtered_logs["Actor"].str.contains(search_query, case=False, na=False) |
            filtered_logs["Action"].str.contains(search_query, case=False, na=False) |
            filtered_logs["IP"].str.contains(search_query, case=False, na=False)
        ]

    st.dataframe(filtered_logs, use_container_width=True, hide_index=True)

    from utils.report_export import render_export_ui
    with st.expander("📥 Export Audit Logs", expanded=False):
        render_export_ui(filtered_logs, filename_prefix="security_audit_logs", title="Security Audit Logs", key_prefix="audit_exp")


def render_ip_whitelist_tab() -> None:
    """Render IP Whitelisting and CIDR access rule manager."""
    section_header("🔒 IP Whitelisting & Access Control", "Restrict platform and API access to authorized CIDR blocks and IP ranges")

    if "ip_whitelist" not in st.session_state:
        st.session_state["ip_whitelist"] = [
            {"CIDR/IP": "192.168.1.0/24", "Label": "HQ Office Subnet", "Status": "Active", "Added By": "Admin", "Date": "2026-01-15"},
            {"CIDR/IP": "10.0.4.0/22", "Label": "Mall Local Network", "Status": "Active", "Added By": "Admin", "Date": "2026-02-01"},
            {"CIDR/IP": "52.92.102.44/32", "Label": "POS Gateway Server", "Status": "Active", "Added By": "Alex Morgan", "Date": "2026-03-10"},
        ]

    whitelist_df = pd.DataFrame(st.session_state["ip_whitelist"])
    st.dataframe(whitelist_df, use_container_width=True, hide_index=True)

    with st.expander("➕ Add IP / CIDR Rule", expanded=True):
        with st.form("add_ip_form"):
            ip_val = st.text_input("IP Address or CIDR Range", placeholder="e.g. 203.0.113.0/24")
            label_val = st.text_input("Description / Label", placeholder="e.g. Branch Office")
            added = st.form_submit_button("Add Whitelist Rule", type="primary", use_container_width=True)
            if added:
                if ip_val and label_val:
                    st.session_state["ip_whitelist"].append({
                        "CIDR/IP": ip_val, "Label": label_val, "Status": "Active", "Added By": "Current User", "Date": datetime.now().strftime("%Y-%m-%d")
                    })
                    st.success(f"Added **{ip_val}** ({label_val}) to IP whitelist.")
                    st.rerun()
                else:
                    st.error("Please provide both IP/CIDR range and a description label.")


def render_rbac_matrix_tab() -> None:
    """Render Role-Based Access Control (RBAC) permission matrix."""
    section_header("🔑 Role-Based Access Control (RBAC) Matrix", "Inspect and configure fine-grained permissions per user persona")

    rbac_data = {
        "Permission / Feature": [
            "View Executive Dashboard",
            "Access Raw Transaction Data",
            "Export PDF / Excel Reports",
            "Manage Tenant Leases",
            "Trigger ML Retraining & Simulations",
            "Manage API Keys & SSO Settings",
            "View Facilities Security Cameras",
            "Modify IP Whitelists & Roles",
        ],
        "Admin": ["✅ Full", "✅ Full", "✅ Full", "✅ Full", "✅ Full", "✅ Full", "✅ Full", "✅ Full"],
        "Data Analyst": ["✅ Full", "✅ Full", "✅ Full", "❌ No", "✅ Full", "❌ No", "❌ No", "❌ No"],
        "Store Manager": ["✅ View", "⚠️ Scoped", "✅ Scoped", "✅ View", "❌ No", "❌ No", "❌ No", "❌ No"],
        "Viewer": ["✅ View", "❌ No", "⚠️ PDF Only", "❌ No", "❌ No", "❌ No", "❌ No", "❌ No"],
    }
    st.dataframe(pd.DataFrame(rbac_data), use_container_width=True, hide_index=True)
    st.info("💡 Roles can be customized per organization. Contact System Administrator to add custom RBAC policies.")


def main() -> None:
    """Bootstrap and render Facilities & Security Operations page."""
    bootstrap_page(
        "Facilities Operations",
        "admin",
        breadcrumbs=["Operations", "Facilities & Admin"],
        subtitle="Roster, equipment health, incidents, security audit logs, and access control",
        icon="🛠️",
    )

    hero_section(
        "Facilities & Security Operations",
        "Keep the mall running safely and smoothly by managing security staff rosters, monitoring HVAC and escalator systems, logging security incidents, and controlling platform access rules.",
        [("View Security Cameras", "video"), ("Log Incident", "alert-triangle")],
    )

    alert_banner("warning", "HVAC Fault – Food Court", "HVAC unit in Food Court Zone A is operating at 40% capacity. Technician dispatched.")

    metric_grid([
        {"label": "Security Staff On Duty", "value": "24", "change": 4.0, "icon": "shield", "tone": "primary"},
        {"label": "Systems Online", "value": "6/7", "change": 0, "icon": "hard-drive", "tone": "warning"},
        {"label": "Incidents Today", "value": "4", "change": -2.0, "icon": "alert-triangle", "tone": "success"},
        {"label": "Mall Open Duration", "value": "6h 42m", "change": 0, "icon": "clock", "tone": "neutral"},
    ], columns=4)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Staff Roster", "Facilities Status", "Systems Health", "Incident Log", "📋 Audit Log", "🔒 IP Whitelist", "🔑 RBAC Matrix"
    ])

    with tab1:
        render_roster_tab()
    with tab2:
        render_facilities_tab()
    with tab3:
        render_hardware_tab()
    with tab4:
        render_incident_tab()
    with tab5:
        render_audit_log_tab()
    with tab6:
        render_ip_whitelist_tab()
    with tab7:
        render_rbac_matrix_tab()

    finish_page()


main()

