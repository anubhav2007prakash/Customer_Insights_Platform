"""Mall Events & Campaigns — OmniMall AI."""

from __future__ import annotations

import streamlit as st

from components.charts.chart_factory import bar_chart, pie_chart
from components.ui.cards import alert_banner, hero_section, metric_grid, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_campaign_performance, get_traffic_sources


def render_events_tab() -> None:
    """Render live mall event and campaign performance details."""
    section_header("Live Mall Event Performance", "Track ongoing events and promotional campaigns across the mall")
    st.markdown('<div class="if-card">', unsafe_allow_html=True)

    df = get_campaign_performance()
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        bar_chart(df, "campaign", "footfall_lift", "Footfall Lift by Campaign")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        bar_chart(df, "campaign", "roi", "ROI by Campaign")
        st.markdown("</div>", unsafe_allow_html=True)


def render_traffic_tab() -> None:
    """Render footfall and visitor traffic attribution."""
    section_header("Visitor Traffic Attribution", "Where are your mall visitors coming from?")

    df = get_traffic_sources()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        pie_chart(df, "source", "entries", "Visitor Entries by Gate / Channel")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        bar_chart(df, "source", "conversion", "Purchase Conversion by Entry Point")
        st.markdown("</div>", unsafe_allow_html=True)


def render_create_event_tab() -> None:
    """Render new mall event / campaign creation form."""
    section_header("Launch a New Mall Event", "Instantly create and push a new event or promotional campaign to the loyalty app and signage")

    # Active event codes
    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    st.dataframe(
        {
            "Event Name": ["Holiday Lights Display", "Weekend Farmers Market", "Black Friday Extravaganza"],
            "Offer": ["2× Loyalty Points", "Free Parking", "$50 Gift Card Entry"],
            "Status": ["✅ Active", "✅ Active", "⏳ Upcoming"],
            "Registrations": [8200, 3400, 12800],
        },
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    with st.form("create_event_form"):
        st.markdown("**Create a New Event or Campaign**")
        c1, c2 = st.columns(2)
        with c1:
            event_name = st.text_input("Event Name", placeholder="e.g. Spring Fashion Week")
            event_type = st.selectbox("Event Type", ["Mall-Wide Sale", "Themed Event", "Live Entertainment", "Anchor Store Launch", "Seasonal Promotion", "Community Event"])
            zone = st.selectbox("Primary Zone", ["All Zones", "North Wing", "South Wing", "Food Court", "Atrium", "Parking Area"])
        with c2:
            offer = st.text_input("Loyalty Offer / Incentive", placeholder="e.g. 2× Points on all purchases")
            duration = st.selectbox("Duration", ["1 Day", "Weekend", "1 Week", "Full Month", "Ongoing"])
            budget = st.number_input("Campaign Budget ($)", min_value=0, value=5000)

        push_app = st.checkbox("Push notification to Mall Loyalty App", value=True)
        push_signage = st.checkbox("Display on Mall Digital Signage", value=True)

        submitted = st.form_submit_button("Launch Campaign", type="primary")
        if submitted:
            if not event_name:
                st.error("Please enter an event name.")
            else:
                channels = []
                if push_app:
                    channels.append("Loyalty App")
                if push_signage:
                    channels.append("Digital Signage")
                ch_str = " & ".join(channels) if channels else "no channels"
                st.success(f"🎉 **{event_name}** launched for {duration} across **{zone}**! Pushed to: {ch_str}. Budget: ${budget:,}.")


def main() -> None:
    """Bootstrap and render Mall Events & Campaigns page."""
    bootstrap_page(
        "Mall Events & Campaigns",
        "marketing",
        breadcrumbs=["Marketing & Loyalty", "Mall Campaigns"],
        subtitle="Manage mall-wide events, loyalty promotions, and visitor traffic attribution",
        icon="🎉",
    )

    role = st.session_state.get("if_user_role", "Admin")

    hero_section(
        "Mall Events & Campaigns Engine",
        "Plan and track mall-wide promotional events, analyze their footfall lift and ROI, and instantly launch new campaigns directly to the loyalty app and digital signage.",
        [("Review Live Events", "megaphone"), ("Launch New Campaign", "zap")],
    )

    alert_banner("success", "Holiday Lights Performing Well", "The 'Holiday Lights Display' event is driving a 28% footfall lift vs. baseline weekends.")

    metric_grid([
        {"label": "Campaign ROI", "value": "4.2×", "change": 14.4, "icon": "trending-up", "tone": "primary"},
        {"label": "Event Footfall Lift", "value": "+28%", "change": 5.8, "icon": "users", "tone": "success"},
        {"label": "Campaign Spend (MTD)", "value": "$42,800", "change": -3.2, "icon": "dollar-sign", "tone": "warning"},
        {"label": "Loyalty App Reach", "value": "82,400", "change": 12.5, "icon": "smartphone", "tone": "accent"},
    ], columns=4)

def render_ab_testing_tab() -> None:
    """Render A/B experiment comparison cards."""
    section_header("A/B Campaign Experiments", "Statistically validated variant comparisons")

    ab_tests = [
        {
            "name": "Weekend Push Notification Wording",
            "stat": "98.4% Confidence",
            "winner": "Variant B (2x Loyalty Points)",
            "a_metrics": "Variant A: 12.4% Open Rate | 2.1% Visit",
            "b_metrics": "Variant B: 19.8% Open Rate | 4.8% Visit",
            "lift": "+64% Lift in App Conversions",
            "status": "Completed — Auto-promoted B",
        },
        {
            "name": "Digital Signage Hero Banner Design",
            "stat": "84.1% Confidence (In Progress)",
            "winner": "Variant A (Dynamic Video)",
            "a_metrics": "Variant A: 48s Dwell Time | 14.2% QR Scan",
            "b_metrics": "Variant B: 31s Dwell Time | 8.9% QR Scan",
            "lift": "+59% Scan Rate",
            "status": "Running — 4 days left",
        },
    ]

    for test in ab_tests:
        st.html(
            f"""
            <div class="if-card" style="margin-bottom: 16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-weight:700; font-size:15px; color:#0f1028;">🧪 {test['name']}</span>
                    <span class="if-badge primary">{test['stat']}</span>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 12px 0;">
                    <div style="background:rgba(99,102,241,0.05); padding:12px; border-radius:10px; border:1px solid rgba(99,102,241,0.15);">
                        <div style="font-size:11px; font-weight:700; color:#6b7280;">CONTROL / VARIANT A</div>
                        <div style="font-size:12px; color:#374151; margin-top:4px;">{test['a_metrics']}</div>
                    </div>
                    <div style="background:rgba(16,185,129,0.06); padding:12px; border-radius:10px; border:1px solid rgba(16,185,129,0.2);">
                        <div style="font-size:11px; font-weight:700; color:#10b981;">WINNER / VARIANT B ⭐</div>
                        <div style="font-size:12px; color:#374151; margin-top:4px;">{test['b_metrics']}</div>
                    </div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:12px;">
                    <span style="color:#10b981; font-weight:700;">🚀 {test['lift']}</span>
                    <span style="color:#6b7280;">Status: {test['status']}</span>
                </div>
            </div>
            """
        )


def main() -> None:
    """Bootstrap and render Marketing page."""
    bootstrap_page(
        "Events & Marketing",
        "marketing",
        breadcrumbs=["Marketing & Loyalty", "Events & Campaigns"],
        subtitle="Manage mall-wide campaigns, traffic sources, and promotional offers",
        icon="🎯",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)

    hero_section(
        "Mall Events & Promotional Campaigns",
        "Design, publish, and measure promotional events across digital signage, the loyalty mobile app, and SMS alerts to drive tenant footfall.",
        [("Launch Campaign", "plus-circle"), ("View Traffic Sources", "bar-chart-3")],
    )

    alert_banner("info", "Campaign Active", "Black Friday Extravaganza prep campaign is currently running across 42 digital screens.")

    metric_grid([
        {"label": "Active Campaigns", "value": "6", "change": 2.0, "icon": "target", "tone": "primary"},
        {"label": "Avg Footfall Lift", "value": "+18.4%", "change": 3.1, "icon": "trending-up", "tone": "success"},
        {"label": "Campaign Spend (MTD)", "value": "$42,800", "change": -3.2, "icon": "dollar-sign", "tone": "warning"},
        {"label": "Loyalty App Reach", "value": "82,400", "change": 12.5, "icon": "smartphone", "tone": "accent"},
    ], columns=4)

    tab1, tab2, tab3, tab4 = st.tabs(["Live Events", "Traffic Attribution", "Launch Campaign", "🧪 A/B Experiments"])

    with tab1:
        render_events_tab()
    with tab2:
        render_traffic_tab()
    with tab3:
        render_create_event_tab()
    with tab4:
        render_ab_testing_tab()

    finish_page()


main()
