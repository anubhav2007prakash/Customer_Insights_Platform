"""Segmentation — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.charts.chart_factory import pie_chart, scatter_chart, treemap_chart
from components.ui.cards import metric_grid, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_customers, get_top_segments


def render_segment_overview() -> None:
    """Render general segment performance distribution charts."""
    section_header("Segment Overview")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        pie_chart(get_top_segments(), "segment", "customers", "Customer Distribution")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        treemap_chart(get_top_segments(), ["segment"], "revenue", "Revenue by Segment")
        st.markdown("</div>", unsafe_allow_html=True)


def render_segment_builder() -> None:
    """Render segment builder setup form."""
    section_header("Segment Builder")
    with st.expander("Create new segment", expanded=True):
        with st.form("create_segment_form"):
            c3, c4, c5 = st.columns(3)
            with c3:
                st.multiselect("Criteria", ["LTV > $10K", "Health Score > 80", "Last active < 30d", "Enterprise"], key="seg_builder_criteria")
            with c4:
                st.selectbox("Logic", ["AND", "OR"], key="seg_builder_logic")
            with c5:
                name = st.text_input("Segment name", placeholder="High Value Active", key="seg_builder_name")

            submitted = st.form_submit_button("Build Custom Segment", type="primary", use_container_width=True)
            if submitted:
                if not name:
                    st.error("Please enter a name for the custom segment.")
                else:
                    st.success(f"Custom segment **{name}** built successfully and added to active segments database.")
                    st.session_state["if_custom_segment_name"] = name


def main() -> None:
    """Bootstrap and render Segmentation page."""
    bootstrap_page(
        "Segmentation",
        "customers",
        breadcrumbs=["Customers", "Segmentation"],
        subtitle="Dynamic customer segments powered by ML clustering",
        icon="🧩",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    section_header(f"{dashboard_context['hero_title']} — segmentation")

    metric_grid([
        {"label": "Active Segments", "value": "25" if st.session_state.get("if_custom_segment_name") else "24", "change": 4.1 if st.session_state.get("if_custom_segment_name") else 3.0, "icon": "layers", "tone": "primary"},
        {"label": "Avg Segment Size", "value": "2,012", "change": 5.4, "icon": "users", "tone": "accent"},
        {"label": "Silhouette Score", "value": "0.82", "change": 0.3, "icon": "target", "tone": "success"},
        {"label": "Last Updated", "value": "Just now" if st.session_state.get("if_custom_segment_name") else "2h ago", "change": 0, "icon": "clock", "tone": "neutral"},
    ], columns=4)

    render_segment_overview()
    render_segment_builder()

    cust = get_customers(100)
    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    scatter_chart(cust, "health_score", "ltv", "segment", "orders", 400)
    st.markdown("</div>", unsafe_allow_html=True)

    finish_page()


main()
