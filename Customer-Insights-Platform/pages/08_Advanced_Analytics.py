"""Advanced Analytics — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.charts.chart_factory import (
    radar_chart, sankey_chart, scatter_chart, treemap_chart, box_plot, multi_line_chart,
)
from components.ui.cards import section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_analytics_metrics, get_revenue_trend


def render_flow_hierarchy(metrics) -> None:
    """Render conversion flow and revenue treemap hierarchy."""
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        sankey_chart(
            labels=["Visitors", "Leads", "MQL", "SQL", "Opportunity", "Closed"],
            source=[0, 1, 2, 3, 4],
            target=[1, 2, 3, 4, 5],
            values=[125000, 42000, 18500, 6200, 2840],
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        treemap_chart(metrics, ["region", "product"], "revenue", "Revenue Hierarchy")
        st.markdown("</div>", unsafe_allow_html=True)


def render_comparative_analysis(metrics) -> None:
    """Render performance radar and scatter analysis."""
    section_header("Comparative Analysis")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        radar_chart(
            ["Revenue", "Margin", "Volume", "Growth", "Retention"],
            [92, 78, 85, 88, 76],
            "Performance Radar",
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        scatter_chart(metrics, "margin", "revenue", "product", "units", 380)
        st.markdown("</div>", unsafe_allow_html=True)


def render_statistical_distribution(metrics) -> None:
    """Render time series and box plots for distributions."""
    section_header("Statistical Distribution")
    rev = get_revenue_trend()
    rev["week"] = rev["date"].dt.isocalendar().week.astype(str)
    weekly = rev.groupby("week").agg({"revenue": "mean", "orders": "sum"}).reset_index()

    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    multi_line_chart(weekly.head(12), "week", ["revenue", "orders"], "Weekly Metrics")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    box_plot(metrics, "product", "revenue", "Revenue Distribution by Product")
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Bootstrap and render Advanced Analytics page."""
    bootstrap_page(
        "Advanced Analytics",
        "advanced",
        breadcrumbs=["Analytics", "Advanced Analytics"],
        subtitle="Deep-dive analysis with Sankey, treemap, radar, and cohort views",
        icon="🔬",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    section_header(f"{dashboard_context['hero_title']} — advanced analytics")

    metrics = get_analytics_metrics()

    render_flow_hierarchy(metrics)
    render_comparative_analysis(metrics)
    render_statistical_distribution(metrics)

    finish_page()


main()
