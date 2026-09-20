"""Customer Intelligence — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.charts.chart_factory import heatmap_chart, radar_chart, treemap_chart
from components.ui.cards import alert_banner, hero_section, insight_card, metric_grid, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_heatmap_data, get_top_segments


def render_segment_analysis() -> None:
    """Render the segment analysis charts."""
    section_header("Segment analysis", "Where the next growth pockets appear")
    left, right = st.columns([1.1, 0.9])
    with left:
        st.html(
            """
            <div class="if-story-card if-fade-in">
                <div class="if-story-head">
                    <div class="if-story-title">Revenue by segment</div>
                    <span class="if-badge success">Live</span>
                </div>
                <div class="if-story-copy">Enterprise and mid-market segments continue to outperform baseline, with strongest expansion in the premium tier.</div>
            </div>
            """
        )
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        treemap_chart(get_top_segments(), ["segment"], "revenue", "Revenue Treemap")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        radar_chart(
            ["Engagement", "Retention", "LTV", "Support", "Upsell", "NPS"],
            [85, 78, 92, 70, 88, 76],
            "Segment Health Radar",
        )
        st.markdown("</div>", unsafe_allow_html=True)


def render_engagement_patterns() -> None:
    """Render engagement pattern heatmap."""
    section_header("Engagement patterns", "Timing, intensity, and interaction depth")
    st.html(
        """
        <div class="if-story-card if-fade-in" style="margin-bottom: 12px;">
            <div class="if-story-head">
                <div class="if-story-title">Behavioral signals</div>
                <span class="if-badge neutral">Updated 3m ago</span>
            </div>
            <div class="if-story-copy">High-frequency users tend to convert faster and show stronger expansion potential, especially in the first 14 days after activation.</div>
        </div>
        """
    )
    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    heatmap_chart(get_heatmap_data(), "hour", "day", "engagement", "Engagement Heatmap")
    st.markdown("</div>", unsafe_allow_html=True)


def render_ai_insights() -> None:
    """Render AI-discovered insight cards."""
    section_header("AI-discovered insights", "High-confidence prompts the teams should act on")
    for ins in [
        {"title": "Enterprise expansion signal", "body": "842 enterprise accounts show 3+ product adoption — prime for suite upsell."},
        {"title": "SMB churn pattern", "body": "Accounts with <3 logins in 14 days have 4.2× churn probability."},
        {"title": "Partner channel growth", "body": "Partner-sourced customers have 28% higher LTV than direct acquisition."},
    ]:
        insight_card(ins["title"], ins["body"])


def main() -> None:
    """Bootstrap and render the Customer Intelligence page."""
    bootstrap_page(
        "Customer Intelligence",
        "intelligence",
        breadcrumbs=["Customers", "Customer Intelligence"],
        subtitle="360° view of customer behavior, health, and lifetime value",
        icon="🧠",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    hero_copy = {
        "Data Analyst": "The customer intelligence workspace highlights segment quality, engagement drift, and the strongest expansion signals for analysis.",
        "Data Scientist": "The customer intelligence workspace highlights behavioral clusters, uplift potential, and the next modeling priorities.",
        "Manager": "The customer intelligence workspace highlights the accounts that need attention and the growth motions worth accelerating.",
        "Admin": "The customer intelligence workspace highlights platform-safe customer insights and the controls that protect them.",
    }

    hero_section(
        f"{dashboard_context['hero_title']} — customer intelligence",
        hero_copy.get(role, "The platform is surfacing the most valuable expansion signals, at-risk accounts, and loyalty patterns in one place."),
        [("Review segment playbook", "users"), ("Open health score view", "heart")],
    )

    alert_banner(
        "info",
        "Signal watchlist",
        "Enterprise accounts with rising adoption now carry the highest upsell potential this week.",
    )

    metric_grid([
        {"label": "Total CLV", "value": "$186M", "change": 14.2, "icon": "dollar-sign", "tone": "primary"},
        {"label": "Health Score", "value": "82.4", "change": 2.1, "icon": "heart", "tone": "success"},
        {"label": "Active Segments", "value": "24", "change": 3.0, "icon": "layers", "tone": "accent"},
        {"label": "At-Risk Accounts", "value": "142", "change": -8.5, "icon": "alert-triangle", "tone": "danger"},
    ], columns=4)

    render_segment_analysis()
    render_engagement_patterns()
    render_ai_insights()

    finish_page()


main()
