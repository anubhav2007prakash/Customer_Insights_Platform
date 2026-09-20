"""Mall Traffic Analytics — OmniMall AI."""

from __future__ import annotations

import streamlit as st

from components.charts.chart_factory import (
    bar_chart, box_plot, funnel_chart, gauge_chart, heatmap_chart,
    histogram_chart, line_chart, pie_chart, scatter_chart, sunburst_chart,
)
from components.ui.cards import alert_banner, custom_tabs, hero_section, metric_grid, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_analytics_metrics, get_conversion_funnel, get_heatmap_data, get_revenue_trend


def render_overview_tab(metrics) -> None:
    """Render Overview analytics tab."""
    section_header("Mall Revenue & Footfall", "The story behind momentum, zone performance, and traffic concentration")
    c1, c2 = st.columns([2, 1])
    rev = get_revenue_trend()
    with c1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        line_chart(rev, "date", "revenue", "Tenant Revenue Over Time")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        gauge_chart(91.4, "Occupancy Rate %")
        st.markdown("</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        if "footfall" in metrics.columns and "revenue" in metrics.columns:
            scatter_chart(metrics, "footfall", "revenue", "zone", "rent_yield", 360)
        else:
            scatter_chart(metrics, "footfall", "revenue", "zone", "rent_yield", 360)
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        grp_col = "zone" if "zone" in metrics.columns else metrics.columns[0]
        bar_chart(metrics.groupby(grp_col)["revenue"].sum().reset_index(), grp_col, "revenue", "Revenue by Mall Zone")
        st.markdown("</div>", unsafe_allow_html=True)


def render_distribution_tab(metrics) -> None:
    """Render Distribution analysis tab."""
    section_header("Tenant Category Distribution", "Understand which tenant categories drive the most footfall and revenue")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        histogram_chart(metrics, "revenue", "Revenue Distribution by Tenant")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        grp_col = "zone" if "zone" in metrics.columns else metrics.columns[0]
        box_plot(metrics, grp_col, "revenue", "Revenue Spread by Zone")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    heatmap_chart(get_heatmap_data(), "hour", "day", "engagement", "Mall Footfall Heatmap (by Day & Hour)")
    st.markdown("</div>", unsafe_allow_html=True)


def render_funnel_tab(metrics) -> None:
    """Render Funnel analytics tab."""
    section_header("Mall Visitor Journey Funnel", "See where mall visitors drop off vs. convert to purchasing customers")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        funnel_df = get_conversion_funnel()
        funnel_chart(funnel_df, "count", "stage", "Mall Footfall-to-Purchase Funnel")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        cat_col = "tenant_category" if "tenant_category" in metrics.columns else "zone"
        zone_col = "zone" if "zone" in metrics.columns else metrics.columns[0]
        if cat_col in metrics.columns and zone_col in metrics.columns:
            sunburst_chart(
                metrics.assign(combo=lambda d: d[cat_col] + " / " + d[zone_col]),
                [cat_col, zone_col], "revenue", "Tenant Category × Zone",
            )
        st.markdown("</div>", unsafe_allow_html=True)


def render_geographic_tab(metrics) -> None:
    """Render Zone & segment analytics tab."""
    section_header("Zone & Segment Analysis", "Understand how footfall and revenue are distributed across mall zones")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        grp_col = "zone" if "zone" in metrics.columns else metrics.columns[0]
        pie_chart(metrics.groupby(grp_col)["revenue"].sum().reset_index(), grp_col, "revenue", "Revenue Mix by Zone")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        cat_col = "tenant_category" if "tenant_category" in metrics.columns else grp_col
        bar_chart(metrics.groupby(cat_col)["footfall"].sum().reset_index(), cat_col, "footfall", "Footfall by Tenant Category", horizontal=True)
        st.markdown("</div>", unsafe_allow_html=True)


from utils.report_export import render_export_ui, filter_df_by_date_range
from datetime import date, timedelta


def render_filters():
    """Render dashboard date range presets and query filters."""
    f0, f1, f2, f3, f4 = st.columns([1.5, 1, 1, 1.2, 1.2])
    with f0:
        preset = st.selectbox(
            "Time Horizon",
            ["Last 30 Days", "Last 7 Days", "Year to Date", "Custom Range"],
            key="analytics_date_preset",
        )
    today = date.today()
    if preset == "Last 7 Days":
        default_start, default_end = today - timedelta(days=7), today
    elif preset == "Year to Date":
        default_start, default_end = date(today.year, 1, 1), today
    elif preset == "Custom Range":
        default_start, default_end = today - timedelta(days=30), today
    else:  # Last 30 Days
        default_start, default_end = today - timedelta(days=30), today

    with f1:
        start_date = st.date_input("From", value=default_start, key="analytics_filter_from")
    with f2:
        end_date = st.date_input("To", value=default_end, key="analytics_filter_to")
    with f3:
        zone = st.selectbox("Zone", ["All Zones", "North Wing", "South Wing", "East Wing", "Food Court", "Atrium"], key="analytics_filter_zone")
    with f4:
        category = st.selectbox("Category", ["All Categories", "Apparel", "Electronics", "Food & Bev", "Entertainment", "Beauty"], key="analytics_filter_category")
    return start_date, end_date, zone, category


def main() -> None:
    """Bootstrap and render the Analytics page."""
    bootstrap_page(
        "Mall Traffic Analytics",
        "analytics",
        breadcrumbs=["Mall Operations", "Mall Traffic"],
        subtitle="Deep-dive into mall footfall, tenant zone performance, and visitor conversion rates",
        icon="📊",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)

    hero_section(
        "Mall Traffic Analytics",
        "Analyze visitor behaviour across all mall zones, identify peak footfall hours, and understand which tenant categories drive the most revenue and dwell time.",
        [("Export Traffic Report", "download"), ("View Sensor Dashboard", "video")],
    )

    alert_banner("success", "Analytics updated", "The latest mall footfall and tenant revenue signals have been refreshed dynamically.")

    metric_grid([
        {"label": "Total Footfall", "value": "28,400", "change": 8.1, "icon": "users", "tone": "primary"},
        {"label": "Avg Dwell Time", "value": "124 mins", "change": 4.6, "icon": "clock", "tone": "success"},
        {"label": "Mall Conversion Rate", "value": "28.4%", "change": 1.4, "icon": "zap", "tone": "accent"},
        {"label": "Active Promotions", "value": "7", "change": 2.0, "icon": "tag", "tone": "warning"},
    ], columns=4)

    # Filters
    _start, _end, zone, category = render_filters()

    metrics = get_analytics_metrics()
    if zone != "All Zones" and "zone" in metrics.columns:
        metrics = metrics[metrics["zone"] == zone]
    if category != "All Categories" and "tenant_category" in metrics.columns:
        metrics = metrics[metrics["tenant_category"] == category]

    # Data Export Widget
    with st.expander("📥 Export Options & Report Generation", expanded=False):
        render_export_ui(metrics, filename_prefix="mall_traffic_analytics", title="Mall Traffic Analytics Report", key_prefix="analytics_exp")


    tab_idx = custom_tabs(["Mall Revenue", "Tenant Categories", "Visitor Funnel", "Zone Analysis", "🗺 Heatmap", "📊 Cohort"], "analytics_main")

    if tab_idx == 0:
        render_overview_tab(metrics)
    elif tab_idx == 1:
        render_distribution_tab(metrics)
    elif tab_idx == 2:
        render_funnel_tab(metrics)
    elif tab_idx == 3:
        render_geographic_tab(metrics)
    elif tab_idx == 4:
        # ── #3 Floor Map Heatmap ─────────────────────────────────────────────
        section_header("Mall Floor Heatmap", "Zone intensity by footfall — darker = higher density")
        import plotly.graph_objects as go
        import numpy as np

        hm_metric = st.selectbox("Metric", ["Footfall", "Revenue", "Dwell Time", "Conversion Rate"], key="hm_metric")
        np.random.seed(42)
        zones_rows = ["Level 3", "Level 2", "Level 1", "Ground"]
        zones_cols = ["West", "Central-W", "Atrium", "Central-E", "East"]
        z_data = np.random.randint(30, 100, size=(4, 5)).tolist()
        # Make atrium always hottest
        z_data[1][2] = 98; z_data[2][2] = 94

        fig_hm = go.Figure(go.Heatmap(
            z=z_data, x=zones_cols, y=zones_rows,
            colorscale=[[0, "#e0f2fe"], [0.4, "#6366f1"], [0.7, "#4f46e5"], [1, "#1e1b4b"]],
            text=[[f"{v}%" for v in row] for row in z_data],
            texttemplate="%{text}", textfont={"size": 14, "color": "white"},
            showscale=True,
            colorbar=dict(title=hm_metric, tickfont=dict(size=11)),
        ))
        fig_hm.update_layout(
            title=f"OmniMall Floor Plan — {hm_metric} Intensity",
            height=380, margin=dict(l=60, r=20, t=44, b=30),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", size=12),
            xaxis=dict(side="top"),
        )
        st.plotly_chart(fig_hm, use_container_width=True)

        hm_c1, hm_c2, hm_c3 = st.columns(3)
        hm_c1.metric("Peak Zone", "Central Atrium", "↑ 34% above avg")
        hm_c2.metric("Quietest Zone", "Level 3 West", "↓ 18% below avg")
        hm_c3.metric("Highest Dwell", "Food Court", "Avg 42 min")
        # ─────────────────────────────────────────────────────────────────────

    else:
        # ── #11 Cohort Retention Table ────────────────────────────────────────
        section_header("Cohort Retention Analysis", "Month-over-month visitor return rates by acquisition cohort")
        import pandas as pd
        import plotly.graph_objects as go
        import numpy as np

        cohort_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        retention = []
        np.random.seed(7)
        for i, m in enumerate(cohort_months):
            row = [100]
            for j in range(1, 6 - i):
                prev = row[-1]
                row.append(max(10, int(prev * np.random.uniform(0.62, 0.82))))
            retention.append(row + [None] * (5 - len(row) + 1))

        col_labels = ["Month 0", "Month 1", "Month 2", "Month 3", "Month 4", "Month 5"]

        def _retention_color(v):
            if v is None: return "rgba(0,0,0,0)"
            if v >= 80: return "#10b981"
            if v >= 60: return "#6366f1"
            if v >= 40: return "#f59e0b"
            return "#ef4444"

        cells_html = ""
        for i, (m, row) in enumerate(zip(cohort_months, retention)):
            cells_html += f'<div style="display:flex;gap:4px;margin-bottom:4px;">'
            cells_html += f'<div style="width:60px;font-size:12px;font-weight:600;display:flex;align-items:center;">{m}</div>'
            for v in row:
                if v is None:
                    cells_html += '<div style="width:72px;height:36px;background:rgba(0,0,0,0.03);border-radius:6px;"></div>'
                else:
                    bg = _retention_color(v)
                    tc = "white" if v < 80 else "white"
                    cells_html += f'<div style="width:72px;height:36px;background:{bg};border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:{tc};">{v}%</div>'
            cells_html += "</div>"

        header_html = '<div style="display:flex;gap:4px;margin-bottom:6px;">'
        header_html += '<div style="width:60px;font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;">Cohort</div>'
        for lbl in col_labels:
            header_html += f'<div style="width:72px;font-size:10px;font-weight:700;color:#6b7280;text-align:center;">{lbl}</div>'
        header_html += '</div>'

        legend_html = '''<div style="display:flex;gap:12px;margin-top:12px;font-size:11px;align-items:center;">
            <span style="display:flex;align-items:center;gap:4px;"><span style="width:12px;height:12px;background:#10b981;border-radius:3px;display:inline-block;"></span>≥80% Retained</span>
            <span style="display:flex;align-items:center;gap:4px;"><span style="width:12px;height:12px;background:#6366f1;border-radius:3px;display:inline-block;"></span>60–79%</span>
            <span style="display:flex;align-items:center;gap:4px;"><span style="width:12px;height:12px;background:#f59e0b;border-radius:3px;display:inline-block;"></span>40–59%</span>
            <span style="display:flex;align-items:center;gap:4px;"><span style="width:12px;height:12px;background:#ef4444;border-radius:3px;display:inline-block;"></span>&lt;40% At-Risk</span>
        </div>'''

        st.html(f'<div style="background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:18px;">{header_html}{cells_html}{legend_html}</div>')

        co1, co2, co3 = st.columns(3)
        co1.metric("Avg Month-1 Retention", "74%", "↑ 3.2%")
        co2.metric("Best Cohort", "Feb (76%)", "Top performer")
        co3.metric("At-Risk Cohorts", "2", "Jan & Mar Month 4+")
        # ─────────────────────────────────────────────────────────────────────

    finish_page()


main()
