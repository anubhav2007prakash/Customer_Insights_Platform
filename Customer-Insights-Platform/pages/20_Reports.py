"""Reports — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.ui.cards import alert_banner, hero_section, metric_grid, section_header
from utils.helpers import get_dashboard_context, relative_time
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.report_export import build_export_bytes, save_export
from utils.sample_data import get_reports_library, get_scheduled_reports

# ── MIME types ─────────────────────────────────────────────────────────────────
_MIME = {
    "pdf":   "application/pdf",
    "png":   "image/png",
    "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "csv":   "text/csv",
}

# ── Format metadata for the UI ─────────────────────────────────────────────────
_FORMAT_META = {
    "PDF": {
        "icon": "📄",
        "ext": "pdf",
        "desc": "Branded, print-ready report with logo, header, styled table, and footer.",
        "badge": "Recommended",
        "badge_color": "#6366f1",
    },
    "PNG Image": {
        "icon": "🖼️",
        "ext": "png",
        "desc": "High-res dashboard snapshot with charts, metrics, and data preview.",
        "badge": "Visual",
        "badge_color": "#10b981",
    },
    "Excel": {
        "icon": "📊",
        "ext": "xlsx",
        "desc": "Styled spreadsheet with frozen header, auto-width columns, and colour coding.",
        "badge": "Interactive",
        "badge_color": "#2563eb",
    },
    "CSV": {
        "icon": "📃",
        "ext": "csv",
        "desc": "Lightweight raw data export, compatible with any data tool.",
        "badge": "Universal",
        "badge_color": "#6b7280",
    },
}


def _format_card_html(fmt_name: str, meta: dict, selected: bool) -> str:
    """Render a format selector card in HTML."""
    border = "#6366f1" if selected else "#e5e7eb"
    bg = "linear-gradient(135deg,rgba(99,102,241,0.08),rgba(37,99,235,0.04))" if selected else "#fff"
    shadow = "0 0 0 2px rgba(99,102,241,0.25)" if selected else "0 1px 4px rgba(15,23,42,0.06)"
    badge_bg = meta["badge_color"]
    return f"""
    <div style="
        border:1.5px solid {border};
        background:{bg};
        border-radius:14px;
        padding:14px 14px 12px;
        box-shadow:{shadow};
        transition:all 0.18s ease;
        min-height:110px;
    ">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:6px;">
            <span style="font-size:22px;">{meta['icon']}</span>
            <span style="
                font-size:10px;font-weight:700;letter-spacing:0.04em;
                background:{badge_bg};color:#fff;
                padding:2px 8px;border-radius:20px;
            ">{meta['badge']}</span>
        </div>
        <div style="font-size:13px;font-weight:700;color:#0f1028;margin-bottom:3px;">{fmt_name}</div>
        <div style="font-size:11px;color:#6b7280;line-height:1.4;">{meta['desc']}</div>
    </div>
    """


@st.dialog("Download Report", width="large")
def show_download_dialog(reports, report_name: str = "Executive Summary"):
    """Rich download dialog with format cards and live preview."""

    # ── Format picker ──────────────────────────────────────────────────────────
    fmt_names = list(_FORMAT_META.keys())
    if "dl_fmt" not in st.session_state:
        st.session_state["dl_fmt"] = "PDF"

    st.markdown(
        '<div style="font-size:11px;font-weight:700;letter-spacing:0.08em;'
        'text-transform:uppercase;color:#6b7280;margin-bottom:8px;">'
        'SELECT FORMAT</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(len(fmt_names))
    for i, name in enumerate(fmt_names):
        with cols[i]:
            is_sel = st.session_state["dl_fmt"] == name
            st.html(_format_card_html(name, _FORMAT_META[name], is_sel))
            if st.button(
                "✓ Selected" if is_sel else "Select",
                key=f"fmt_btn_{name}",
                use_container_width=True,
                type="primary" if is_sel else "secondary",
            ):
                st.session_state["dl_fmt"] = name
                st.rerun()

    st.divider()

    # ── Options row ────────────────────────────────────────────────────────────
    selected_fmt = st.session_state["dl_fmt"]
    meta = _FORMAT_META[selected_fmt]

    c1, c2 = st.columns([1.4, 0.6])
    with c1:
        filename = st.text_input(
            "File name (without extension)",
            value=report_name.lower().replace(" ", "-"),
            placeholder="my-report",
            key="dl_filename",
        )
    with c2:
        rows_limit = st.number_input(
            "Max rows", min_value=5, max_value=200, value=50, step=5,
            key="dl_rows_limit",
        )

    report_title = st.text_input(
        "Report title (shown inside the document)",
        value=report_name,
        key="dl_report_title",
    )

    st.markdown(
        f'<div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.18);'
        f'border-radius:10px;padding:10px 14px;font-size:12px;color:#374151;margin:4px 0 12px;">'
        f'{meta["icon"]} &nbsp;<strong>{selected_fmt}</strong> — {meta["desc"]}</div>',
        unsafe_allow_html=True,
    )

    # ── Generate & download ────────────────────────────────────────────────────
    if st.button("⚡ Generate & Download", type="primary", use_container_width=True):
        fmt_key = meta["ext"]
        fmt_label = selected_fmt  # e.g. "PNG Image" → need "png" key
        if selected_fmt == "PNG Image":
            fmt_key = "png"
        elif selected_fmt == "Excel":
            fmt_key = "excel"

        with st.spinner(f"Building your {selected_fmt} report…"):
            try:
                payload, ext = build_export_bytes(
                    reports.head(int(rows_limit)),
                    fmt_key,
                    title=report_title or report_name,
                    subtitle="OmniMall AI · InsightForge Platform",
                )
                fname = f"{(filename or 'report').strip()}.{ext}"
                mime = _MIME.get(fmt_key, "application/octet-stream")

                st.success(f"✅ {selected_fmt} report ready — {len(payload):,} bytes")

                st.download_button(
                    label=f"💾  Save  {fname}",
                    data=payload,
                    file_name=fname,
                    mime=mime,
                    use_container_width=True,
                    type="primary",
                    key="final_download_btn",
                )

                # Quick file-size info strip
                size_kb = len(payload) / 1024
                st.html(
                    f"""<div style="display:flex;gap:12px;margin-top:8px;font-size:11px;color:#6b7280;">
                        <span>📁 <strong>{fname}</strong></span>
                        <span>·</span>
                        <span>{size_kb:.1f} KB</span>
                        <span>·</span>
                        <span>{selected_fmt} format</span>
                    </div>"""
                )
            except Exception as exc:
                st.error(f"Export failed: {exc}")


def render_library_tab(reports) -> None:
    """Render the report library list and quick export tools."""
    section_header("Report library", "Trusted snapshots and analysis packs")

    # Per-row download buttons
    display_df = reports.copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.html('<div style="height:12px;"></div>')

    st.markdown(
        """
        <div style="
            background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(37,99,235,0.04));
            border:1px solid rgba(99,102,241,0.18);
            border-radius:14px;padding:20px 20px 16px;
        ">
            <div style="font-size:15px;font-weight:700;color:#0f1028;margin-bottom:4px;">
                Quick Export
            </div>
            <div style="font-size:12px;color:#6b7280;margin-bottom:14px;">
                Download any report as PDF, Image, Excel, or CSV in one click.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    def _quick_dl(col, fmt_key, label, icon, mime_key):
        with col:
            if st.button(f"{icon} {label}", use_container_width=True, key=f"quick_{fmt_key}"):
                with st.spinner(f"Building {label}…"):
                    payload, ext = build_export_bytes(
                        reports.head(50), fmt_key,
                        title="Executive Summary",
                        subtitle="OmniMall AI · InsightForge Platform",
                    )
                    st.download_button(
                        label=f"Save {label}",
                        data=payload,
                        file_name=f"executive-summary.{ext}",
                        mime=_MIME.get(mime_key, "application/octet-stream"),
                        use_container_width=True,
                        key=f"dl_{fmt_key}",
                    )

    _quick_dl(c1, "pdf",   "PDF Report",    "📄", "pdf")
    _quick_dl(c2, "png",   "PNG Image",     "🖼️", "png")
    _quick_dl(c3, "excel", "Excel Sheet",   "📊", "excel")
    _quick_dl(c4, "csv",   "CSV Export",    "📃", "csv")

    st.html('<div style="height:10px;"></div>')
    if st.button("⚙️ Advanced download options…", use_container_width=True):
        show_download_dialog(reports)


def render_templates_tab() -> None:
    """Render standard template cards."""
    section_header("Report templates", "Start from a production-ready format")
    templates = [
        ("Executive Summary",  "📊", "High-level KPIs, footfall, and revenue"),
        ("Customer Health",    "❤️", "Loyalty, churn risk, and engagement"),
        ("Campaign ROI",       "🎯", "Marketing spend vs. conversion lift"),
        ("Sales Pipeline",     "💰", "Tenant sales aggregation and trends"),
        ("Churn Analysis",     "📉", "At-risk tenants with intervention signals"),
        ("Financial Overview", "🏦", "P&L snapshot, occupancy, and lease status"),
    ]
    cols = st.columns(3)
    for i, (name, ico, desc) in enumerate(templates):
        with cols[i % 3]:
            selected = st.session_state.get("if_selected_template") == name
            border = "#6366f1" if selected else "#e5e7eb"
            bg = "rgba(99,102,241,0.06)" if selected else "#fff"
            st.html(
                f"""<div style="
                    border:1.5px solid {border};background:{bg};
                    border-radius:14px;padding:16px;margin-bottom:2px;
                ">
                    <div style="font-size:24px;margin-bottom:6px;">{ico}</div>
                    <div style="font-size:13px;font-weight:700;color:#0f1028;">{name}</div>
                    <div style="font-size:11px;color:#6b7280;margin-top:3px;">{desc}</div>
                </div>"""
            )
            if st.button("Use template", key=f"tpl_{i}", use_container_width=True,
                         type="primary" if selected else "secondary"):
                st.session_state["if_selected_template"] = name
                st.success(f"Loaded **{name}** — configure and export in the Export Center.")
                st.rerun()


def render_scheduled_tab() -> None:
    """Render upcoming scheduled report distributions."""
    section_header("Scheduled reports", "Worry less about hand-offs and more about decisions")
    sched = get_scheduled_reports()
    sched["next_run"] = sched["next_run"].apply(lambda x: x.strftime("%b %d, %Y %H:%M"))
    st.dataframe(sched, use_container_width=True, hide_index=True)


def render_export_center_tab(reports) -> None:
    """Render advanced multi-section export setup form."""
    section_header("Export center", "Build the package your team needs in one pass")

    with st.form("export_center_form"):
        c1, c2 = st.columns(2)
        with c1:
            selected_rep = st.selectbox("Report", reports["name"].tolist(), key="ec_report")
            export_format = st.selectbox(
                "Format", ["PDF", "PNG Image", "Excel", "CSV"], key="export_center_format"
            )
            report_title = st.text_input("Report title", value=selected_rep, key="ec_title")
        with c2:
            st.date_input("Date range", key="ec_date_range")
            st.multiselect(
                "Include sections",
                ["KPIs", "Charts", "Tables", "AI Insights"],
                default=["KPIs", "Charts"],
                key="ec_sections",
            )
            rows_limit = st.number_input("Max rows", min_value=5, max_value=500, value=100, step=10)

        submitted = st.form_submit_button(
            "⚡ Generate Export Package", type="primary", use_container_width=True
        )
        if submitted:
            fmt_key = export_format.lower().replace(" image", "").replace(" ", "")
            if fmt_key == "pngimage" or fmt_key == "png":
                fmt_key = "png"

            with st.spinner(f"Building {export_format} package…"):
                payload, ext = build_export_bytes(
                    reports.head(int(rows_limit)),
                    fmt_key,
                    title=report_title or selected_rep,
                    subtitle="OmniMall AI · InsightForge Platform",
                )
                stem = selected_rep.lower().replace(" ", "-")
                fname = f"export-{stem}.{ext}"
                mime = _MIME.get(fmt_key, "application/octet-stream")
                size_kb = len(payload) / 1024

            st.success(f"✅ Export ready — **{fname}** ({size_kb:.1f} KB)")
            st.download_button(
                label=f"💾  Download  {fname}",
                data=payload,
                file_name=fname,
                mime=mime,
                use_container_width=True,
                type="primary",
                key="ec_download_btn",
            )
            st.html(
                f"""<div style="display:flex;gap:16px;margin-top:8px;
                    font-size:11px;color:#6b7280;align-items:center;">
                    <span>📁 <strong>{fname}</strong></span>
                    <span>·</span><span>{size_kb:.1f} KB</span>
                    <span>·</span><span>{export_format}</span>
                </div>"""
            )

    st.divider()

    # ── #19 Email Delivery ───────────────────────────────────────────────────
    section_header("📧 Email Delivery & Distribution", "Automatically dispatch reports to stakeholders")
    with st.form("email_delivery_form"):
        ec1, ec2 = st.columns(2)
        with ec1:
            recipients = st.text_input("Recipients (comma separated)", value="alex.morgan@acmecorp.com, leadership@omnimall.ai")
            email_subj = st.text_input("Email subject", value=f"OmniMall AI Report: {selected_rep if 'selected_rep' in locals() else 'Executive Summary'}")
        with ec2:
            schedule_freq = st.selectbox("Recurring Schedule", ["One-time immediate", "Daily at 08:00 AM", "Weekly (Mondays)", "Monthly (1st)"])
            include_link = st.checkbox("Include live dashboard link in email", value=True)
        
        email_sent = st.form_submit_button("✉️ Send Report via Email", type="primary", use_container_width=True)
        if email_sent:
            st.success(f"✅ Report successfully queued for delivery to `{recipients}` ({schedule_freq}).")


def main() -> None:
    """Bootstrap and render Reports catalog page."""
    bootstrap_page(
        "Reports",
        "reports",
        breadcrumbs=["Data", "Reports"],
        subtitle="Report library, templates, scheduling, and export center",
        icon="📄",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    hero_copy = {
        "Data Analyst": "The reporting workspace highlights the most relevant export and review workflows for every analysis audience.",
        "Data Scientist": "The reporting workspace highlights template-ready outputs and the evidence that supports experiments and models.",
        "Manager": "The reporting workspace highlights the recurring updates and share-ready packages leadership needs most.",
        "Admin": "The reporting workspace highlights governance-safe reporting and the controls that keep exports reliable.",
    }

    hero_section(
        f"{dashboard_context['hero_title']} — reports",
        hero_copy.get(role, "Deliver polished exports, reusable templates, and scheduled reporting without leaving the operating workspace."),
        [("Schedule report", "calendar"), ("Open export center", "download")],
    )

    alert_banner("warning", "Delivery queue", "Three recurring reports are scheduled to publish within the next hour.")

    metric_grid([
        {"label": "Library Items",  "value": "28", "change": 8.4, "icon": "files",           "tone": "primary"},
        {"label": "Templates",      "value": "12", "change": 3.1, "icon": "layout-template",  "tone": "accent"},
        {"label": "Scheduled",      "value": "9",  "change": 1.7, "icon": "calendar",         "tone": "success"},
        {"label": "Exports Today",  "value": "41", "change": 5.6, "icon": "download",         "tone": "warning"},
    ], columns=4)

def render_tabular_matrix_tab(reports) -> None:
    """Render a detailed in-app tabular breakdown of reports and data fields."""
    section_header("📊 Detailed Tabular Report Matrix", "Comprehensive multi-column data matrix with field statistics")

    import pandas as pd
    import numpy as np

    # Detailed report data table
    rep_choice = st.selectbox("Select Report to Inspect in Tabular View", reports["name"].tolist(), key="matrix_rep_select")

    st.markdown('<div class="if-card" style="margin-bottom:16px;">', unsafe_allow_html=True)
    st.markdown(f"### 📋 Tabular Breakdown: **{rep_choice}**")

    # Generate rich sample detailed rows
    np.random.seed(42)
    categories = ["Fashion & Apparel", "Electronics & Gadgets", "Food & Beverage", "Beauty & Cosmetics", "Home & Living"]
    zones = ["North Wing A", "South Wing B", "Atrium East", "East Corridor", "Food Court 2"]
    
    detailed_rows = []
    for i in range(1, 31):
        cat = categories[i % len(categories)]
        zn = zones[i % len(zones)]
        rev = float(np.random.randint(12000, 185000))
        ft = int(np.random.randint(450, 6800))
        conv = round(float(np.random.uniform(2.4, 18.2)), 2)
        margin = round(float(np.random.uniform(14.0, 48.0)), 2)

        detailed_rows.append({
            "Record ID": f"REC-{2000+i}",
            "Report Name": rep_choice,
            "Category": cat,
            "Zone": zn,
            "Revenue (₹)": rev,
            "Footfall": ft,
            "Conversion %": conv,
            "Margin %": margin,
            "Status": "Verified" if conv > 5.0 else "Needs Review",
        })

    df_matrix = pd.DataFrame(detailed_rows)

    # Filtering controls
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        cat_filter = st.multiselect("Filter by Category", categories, default=categories, key="mat_cat_filt")
    with fc2:
        status_filter = st.multiselect("Status", ["Verified", "Needs Review"], default=["Verified", "Needs Review"], key="mat_stat_filt")
    with fc3:
        min_rev = st.number_input("Min Revenue (₹)", min_value=0, value=0, step=10000, key="mat_min_rev")

    filtered_df = df_matrix[
        df_matrix["Category"].isin(cat_filter) &
        df_matrix["Status"].isin(status_filter) &
        (df_matrix["Revenue (₹)"] >= min_rev)
    ]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Tabular summary statistics block
    section_header("Field Summary Statistics", "Aggregated metric totals in tabular form")
    
    sum_df = pd.DataFrame({
        "Field Name": ["Revenue (₹)", "Footfall", "Conversion %", "Margin %"],
        "Total Sum": [f"₹{filtered_df['Revenue (₹)'].sum():,.2f}", f"{filtered_df['Footfall'].sum():,}", "—", "—"],
        "Average (Mean)": [f"₹{filtered_df['Revenue (₹)'].mean():,.2f}", f"{filtered_df['Footfall'].mean():,.0f}", f"{filtered_df['Conversion %'].mean():.2f}%", f"{filtered_df['Margin %'].mean():.2f}%"],
        "Minimum": [f"₹{filtered_df['Revenue (₹)'].min():,.2f}", f"{filtered_df['Footfall'].min():,}", f"{filtered_df['Conversion %'].min():.2f}%", f"{filtered_df['Margin %'].min():.2f}%"],
        "Maximum": [f"₹{filtered_df['Revenue (₹)'].max():,.2f}", f"{filtered_df['Footfall'].max():,}", f"{filtered_df['Conversion %'].max():.2f}%", f"{filtered_df['Margin %'].max():.2f}%"],
    })
    st.dataframe(sum_df, use_container_width=True, hide_index=True)


def main() -> None:
    """Bootstrap and render Reports catalog page."""
    bootstrap_page(
        "Reports",
        "reports",
        breadcrumbs=["Data", "Reports"],
        subtitle="Report library, templates, scheduling, tabular matrix, and export center",
        icon="📄",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    hero_copy = {
        "Data Analyst": "The reporting workspace highlights the most relevant export and review workflows for every analysis audience.",
        "Data Scientist": "The reporting workspace highlights template-ready outputs and the evidence that supports experiments and models.",
        "Manager": "The reporting workspace highlights the recurring updates and share-ready packages leadership needs most.",
        "Admin": "The reporting workspace highlights governance-safe reporting and the controls that keep exports reliable.",
    }

    hero_section(
        f"{dashboard_context['hero_title']} — reports",
        hero_copy.get(role, "Deliver polished exports, reusable templates, and scheduled reporting without leaving the operating workspace."),
        [("Schedule report", "calendar"), ("Open export center", "download")],
    )

    alert_banner("warning", "Delivery queue", "Three recurring reports are scheduled to publish within the next hour.")

    metric_grid([
        {"label": "Library Items",  "value": "28", "change": 8.4, "icon": "files",           "tone": "primary"},
        {"label": "Templates",      "value": "12", "change": 3.1, "icon": "layout-template",  "tone": "accent"},
        {"label": "Scheduled",      "value": "9",  "change": 1.7, "icon": "calendar",         "tone": "success"},
        {"label": "Exports Today",  "value": "41", "change": 5.6, "icon": "download",         "tone": "warning"},
    ], columns=4)

    reports = get_reports_library()
    reports["updated"] = reports["updated"].apply(relative_time)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Library", "Templates", "Scheduled", "Export Center", "📊 Tabular Matrix"])

    with tab1:
        render_library_tab(reports)
    with tab2:
        render_templates_tab()
    with tab3:
        render_scheduled_tab()
    with tab4:
        render_export_center_tab(reports)
    with tab5:
        render_tabular_matrix_tab(reports)

    finish_page()


main()
