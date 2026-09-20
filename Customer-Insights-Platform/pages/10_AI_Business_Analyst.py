"""AI Business Analyst — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.charts.chart_factory import bar_chart, line_chart
from components.ui.cards import alert_banner, hero_section, insight_card, metric_grid, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_revenue_trend, get_top_segments


def render_configuration_panel() -> None:
    """Render the configuration options form."""
    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    st.markdown("**Analysis Configuration**")
    with st.form("analyst_config_form"):
        focus = st.selectbox(
            "Focus area",
            ["Revenue", "Churn", "Acquisition", "Product Mix", "Campaign ROI"],
            key="analyst_focus",
        )
        horizon = st.selectbox(
            "Time horizon",
            ["Last 7 days", "Last 30 days", "Last quarter", "YTD"],
            key="analyst_horizon",
        )
        segments = st.multiselect(
            "Segments",
            ["Enterprise", "Mid-Market", "SMB", "Startup"],
            default=["Enterprise"],
            key="analyst_segments",
        )
        submitted = st.form_submit_button("Run Analysis", type="primary", use_container_width=True)
        if submitted:
            st.session_state["if_analyst_ran"] = True
            st.session_state["if_analyst_focus"] = focus
            st.session_state["if_analyst_horizon"] = horizon
            st.session_state["if_analyst_segments"] = segments

    st.markdown("</div>", unsafe_allow_html=True)


def render_executive_summary() -> None:
    """Render executive summary and detailed insights."""
    focus = st.session_state.get("if_analyst_focus", "Revenue")
    horizon = st.session_state.get("if_analyst_horizon", "Last quarter")
    segments = st.session_state.get("if_analyst_segments", ["Enterprise"])

    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    st.markdown("### Executive Summary")
    st.markdown(
        f"Analysis focused on **{focus}** over the **{horizon}** horizon for the **{', '.join(segments)}** segment(s).  \n"
        "Revenue grew **12.4%** period-over-period, exceeding forecast by **4.2%**. "
        "Enterprise upsells contributed **68%** of incremental growth. "
        "Mid-market segment shows early churn signals requiring intervention."
    )
    for ins in [
        {"title": "Key Driver", "body": "Analytics Pro → AI Insights upgrade path converting at 34%."},
        {"title": "Risk Factor", "body": "142 accounts with declining engagement in mid-market."},
        {"title": "Opportunity", "body": "$420K expansion pipeline in enterprise Q3."},
    ]:
        insight_card(ins["title"], ins["body"])
    st.markdown("</div>", unsafe_allow_html=True)


def render_visualizations() -> None:
    """Render supporting charts."""
    section_header("Supporting visualizations", "The evidence behind the recommendation")
    v1, v2 = st.columns(2)
    with v1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        line_chart(get_revenue_trend(60), "date", "revenue", "Revenue Trend")
        st.markdown("</div>", unsafe_allow_html=True)
    with v2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        bar_chart(get_top_segments(), "segment", "ltv", "LTV by Segment")
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Bootstrap and render the AI Business Analyst page."""
    bootstrap_page(
        "AI Business Analyst",
        "ai_analyst",
        breadcrumbs=["AI", "AI Business Analyst"],
        subtitle="Autonomous analysis agent for executive-ready insights",
        icon="🤖",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    hero_copy = {
        "Data Analyst": "The analyst surfaces quality signals, trend calls, and the evidence needed for confident reviews.",
        "Data Scientist": "The analyst surfaces modeling signals, experiment context, and the evidence needed for confident reviews.",
        "Manager": "The analyst surfaces delivery signals, priority gaps, and the evidence needed for confident reviews.",
        "Admin": "The analyst surfaces trust signals, governance posture, and the evidence needed for confident reviews.",
    }

    hero_section(
        f"{dashboard_context['hero_title']} — analyst",
        hero_copy.get(role, "The analyst can now surface leadership-ready signals, quantify opportunity, and highlight the decisions that matter most."),
        [("Run new analysis", "bot"), ("Inspect summary", "sparkles")],
    )

    if st.session_state.get("if_analyst_ran"):
        alert_banner("success", "Analysis Complete", "The new custom analysis run finished successfully.")
    else:
        alert_banner("info", "Agent ready", "The latest analysis run is available and aligned with current growth signals.")

    metric_grid([
        {"label": "Signals Reviewed", "value": "24", "change": 8.6, "icon": "activity", "tone": "primary"},
        {"label": "Risks Flagged", "value": "7", "change": 2.1, "icon": "alert-triangle", "tone": "warning"},
        {"label": "Upsell Opportunities", "value": "3", "change": 5.7, "icon": "trending-up", "tone": "success"},
        {"label": "Confidence", "value": "94%", "change": 1.4, "icon": "target", "tone": "accent"},
    ], columns=4)

    c1, c2 = st.columns([1, 2])
    with c1:
        render_configuration_panel()
    with c2:
        render_executive_summary()

    render_visualizations()

    finish_page()


main()
