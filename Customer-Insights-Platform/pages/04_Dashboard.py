"""Executive Dashboard - InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.charts.chart_factory import (
    area_chart, bar_chart, funnel_chart, geo_map, line_chart, pie_chart,
)
from components.ui.cards import (
    alert_banner, hero_section, insight_card, metric_grid, section_header, timeline,
)
from utils.helpers import format_currency, get_dashboard_context, relative_time
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import (
    get_ai_insights, get_alerts, get_campaign_performance, get_conversion_funnel,
    get_customer_acquisition, get_kpis, get_recent_activities, get_recommendations,
    get_reports_library, get_revenue_trend, get_sales_performance, get_top_cities,
    get_top_products, get_top_segments, get_traffic_sources, get_upcoming_tasks,
)


def render_command_center() -> None:
    """Render the executive command center HTML block."""
    st.html(
        """
    <div class="if-command-center">
      <div class="if-command-grid">
        <div class="if-command-card">
          <div class="if-label">Mall Operations Center</div>
          <div class="if-h3" style="margin-top: 6px;">Foot traffic is steady, and tenant zones are fully active.</div>
          <div class="if-body" style="margin-top: 8px;">The system is highlighting peak traffic at the Food Court, high-value tenant performance, and parking capacity alerts.</div>
          <div class="if-command-chip-row">
            <span class="if-command-chip">● Live footfall</span>
            <span class="if-command-chip">● HVAC sync</span>
            <span class="if-command-chip">● Lease watch</span>
          </div>
        </div>
        <div class="if-command-card">
          <div class="if-command-metric">
            <strong>Today's Footfall</strong>
            <span class="if-command-delta">+8.4%</span>
          </div>
          <div class="if-command-metric">
            <strong>Open Leases</strong>
            <span>12 pending</span>
          </div>
          <div class="if-command-metric">
            <strong>Maintenance Alerts</strong>
            <span>4 items</span>
          </div>
          <div class="if-command-metric">
            <strong>Parking Capacity</strong>
            <span>82%</span>
          </div>
        </div>
      </div>
    </div>
    """
    )


def render_hero_os() -> None:
    """Render the AI-powered OS hero section."""
    st.html(
        """
    <div class="if-hero-os if-fade-in">
        <div>
            <div class="if-hero-kicker">Mall Management System</div>
            <div class="if-hero-title">Intelligent leasing, automated operations.</div>
            <div class="if-hero-copy">The workspace now surfaces real-time footfall, tenant sales aggregations, staff performance, and predictive mall traffic in one continuous flow.</div>
            <div class="if-hero-pulse">
                <span class="if-pulse-pill">Sales ↑ 11.4%</span>
                <span class="if-pulse-pill">Footfall ↑ 14.1%</span>
                <span class="if-pulse-pill">Occupancy 96%</span>
                <span class="if-pulse-pill">Lease Renewals 8</span>
            </div>
        </div>
        <div class="if-hero-side">
            <div class="if-panel-label">Today's Footfall</div>
            <div class="if-panel-value">28,400</div>
            <div class="if-story-copy">Expected 24,000. The surplus was driven by a surge in Food Court traffic and the Weekend Farmers Market.</div>
            <div class="if-panel-grid">
                <div class="if-panel-card">
                    <div class="if-panel-label">Avg Dwell Time</div>
                    <div class="if-panel-value">124 mins</div>
                </div>
                <div class="if-panel-card">
                    <div class="if-panel-label">Parking Flow</div>
                    <div class="if-panel-value">2.1/hr</div>
                </div>
            </div>
            <div class="if-stat-strip">
                <span class="if-badge primary">Live cameras</span>
                <span class="if-badge success">Sensors synced</span>
                <span class="if-badge neutral">Updated now</span>
            </div>
        </div>
    </div>
    """
    )


def render_insight_stories() -> None:
    """Render AI insight and activity story cards."""
    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        st.html(
            """
        <div class="if-story-card if-fade-in">
            <div class="if-story-head">
                <div class="if-story-title">Mall Insights</div>
                <span class="if-badge success">Live</span>
            </div>
            <div class="if-story-copy">Footfall increased during the weekend promo, but North Wing traffic lagged behind the South Wing. A shift in mall event locations is recommended.</div>
            <div style="margin-top: 14px;">
                <div class="if-insight-card">
                    <div class="if-insight-title">⚡ Recommended action</div>
                    <div class="if-insight-body">Deploy popup kiosks to the North Wing atrium for the upcoming holiday rush.</div>
                </div>
                <div class="if-insight-card">
                    <div class="if-insight-title">🧠 Tenant signal</div>
                    <div class="if-insight-body">Churn risk for 3 apparel stores within 60 days based on declining sales velocity.</div>
                </div>
            </div>
        </div>
        """
        )
    with c2:
        st.html(
            """
        <div class="if-story-card if-fade-in">
            <div class="if-story-head">
                <div class="if-story-title">What changed today</div>
                <span class="if-badge neutral">Updated</span>
            </div>
            <div class="if-story-copy">Two leases were renewed, one mall promo launched, and the POS aggregator completed its overnight sync.</div>
            <div class="if-panel-grid">
                <div class="if-panel-card">
                    <div class="if-panel-label">Footfall lift</div>
                    <div class="if-panel-value">+14%</div>
                </div>
                <div class="if-panel-card">
                    <div class="if-panel-label">Lease Inquiries</div>
                    <div class="if-panel-value">18</div>
                </div>
            </div>
        </div>
        """
        )


def render_charts(role: str) -> None:
    """Render the revenue and analytics charts section."""
    import time
    from components.ui.cards import skeleton_loader
    
    role_chart_titles = {
        "Data Analyst": ("Mall traffic & revenue trends", "Acquisition signals", "Mall footfall funnel", "Zone performance"),
        "Data Scientist": ("Model readiness & feature signals", "Experiment signals", "Model impact", "Feature leverage"),
        "Manager": ("Mall revenue & execution pulse", "Mall traffic", "Execution health", "Priority mix"),
        "Admin": ("Sensors & platform health", "Access health", "Platform usage", "Policy coverage"),
    }
    chart_titles = role_chart_titles.get(role, ("Mall revenue & footfall intelligence", "Customer acquisition", "Footfall funnel", "Top Tenants"))

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        section_header(chart_titles[0], "Stories, signals, and the next best action")
    with col2:
        with st.popover("⚙️ Customize View", use_container_width=True):
            st.markdown("**Visible Charts**")
            show_c1 = st.checkbox("Trend Overview", value=st.session_state.get("if_show_c1", True), key="cb_c1")
            show_c2 = st.checkbox("Acquisition Signals", value=st.session_state.get("if_show_c2", True), key="cb_c2")
            show_c3 = st.checkbox("Conversion Funnel", value=st.session_state.get("if_show_c3", True), key="cb_c3")
            show_c4 = st.checkbox("Traffic Mix", value=st.session_state.get("if_show_c4", True), key="cb_c4")
            show_c5 = st.checkbox("Top Products", value=st.session_state.get("if_show_c5", True), key="cb_c5")
            st.session_state["if_show_c1"] = show_c1
            st.session_state["if_show_c2"] = show_c2
            st.session_state["if_show_c3"] = show_c3
            st.session_state["if_show_c4"] = show_c4
            st.session_state["if_show_c5"] = show_c5
    
    # Use placeholders for skeleton loading effect
    chart_col, side_col = st.columns([1.15, 0.85])
    with chart_col:
        chart_ph = st.empty()
        if show_c1:
            with chart_ph.container():
                skeleton_loader("chart")
    with side_col:
        side_ph = st.empty()
        if show_c2:
            with side_ph.container():
                skeleton_loader("chart")
            
    c3, c4, c5 = st.columns(3)
    c3_ph = c3.empty()
    c4_ph = c4.empty()
    c5_ph = c5.empty()
    
    if show_c3:
        with c3_ph.container():
            skeleton_loader("chart")
    if show_c4:
        with c4_ph.container():
            skeleton_loader("chart")
    if show_c5:
        with c5_ph.container():
            skeleton_loader("chart")

    # Simulate loading delay only on first render
    if not st.session_state.get("if_dashboard_loaded"):
        time.sleep(1.2)
        st.session_state["if_dashboard_loaded"] = True

    # Render actual charts
    chart_ph.empty()
    if show_c1:
        with chart_ph.container(border=True):
            area_chart(get_revenue_trend(), "date", "revenue", chart_titles[0])
        
    side_ph.empty()
    if show_c2:
        with side_ph.container(border=True):
            line_chart(get_customer_acquisition(), "month", "new_members", chart_titles[1])
        
    c3_ph.empty()
    if show_c3:
        with c3_ph.container(border=True):
            funnel_chart(get_conversion_funnel(), "count", "stage", chart_titles[2])
        
    c4_ph.empty()
    if show_c4:
        with c4_ph.container(border=True):
            pie_chart(get_traffic_sources(), "source", "entries", chart_titles[3])
        
    c5_ph.empty()
    if show_c5:
        with c5_ph.container(border=True):
            bar_chart(get_top_products(5), "tenant", "revenue", "Top products", horizontal=True)


def render_recommendations_tasks(role: str) -> None:
    """Render recommendations and upcoming tasks."""
    role_recommendation_copy = {
        "Data Analyst": ("Analyst focus", "Quality checks", "Review patterns"),
        "Data Scientist": ("Modeling focus", "Experiment checks", "Model follow-ups"),
        "Manager": ("Execution focus", "Team checkpoints", "Stakeholder follow-ups"),
        "Admin": ("Governance focus", "Access reviews", "Platform checks"),
    }
    recommendation_copy = role_recommendation_copy.get(role, ("Decisioning focus", "Upcoming tasks", "Priority follow-ups"))
    dashboard_context = get_dashboard_context(role)

    section_header(dashboard_context["recommendation_title"], f"{recommendation_copy[0]} — move from reporting to decisioning")
    reco_col, task_col = st.columns([1.1, 0.9])
    with reco_col:
        with st.container(border=True):
            st.markdown(f"**{recommendation_copy[1]}**")
            for rec in get_recommendations():
                st.markdown(
                    f"**{rec['action']}**  \n"
                    f"<span class='if-badge primary'>{rec['impact']} Impact</span> "
                    f"<span class='if-badge neutral'>{rec['segment']}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown("---")
    with task_col:
        with st.container(border=True):
            st.markdown(f"**{recommendation_copy[2]}**")
            for task in get_upcoming_tasks():
                st.markdown(
                    f"**{task['task']}**  \n"
                    f"<span class='if-caption'>Due {task['due'].strftime('%b %d')} - </span>"
                    f"<span class='if-badge {'danger' if task['priority'] == 'High' else 'warning' if task['priority'] == 'Medium' else 'neutral'}'>"
                    f"{task['priority']}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown("---")


def render_activity_reports() -> None:
    """Render recent activity and pinned reports."""
    section_header("Customer & Activity Intelligence", "A working surface for teams in motion")
    activity_col, reports_col = st.columns([1.1, 0.9])
    with activity_col:
        with st.container(border=True):
            st.markdown("**Recent activity**")
            timeline(get_recent_activities(6))
    with reports_col:
        with st.container(border=True):
            st.markdown("**Pinned reports**")
            pinned = get_reports_library()
            pinned = pinned[pinned["pinned"]]
            st.dataframe(pinned[["name", "type", "format"]], use_container_width=True, hide_index=True)


def main() -> None:
    """Bootstrap and render the Dashboard page."""
    bootstrap_page(
        "Dashboard",
        "dashboard",
        breadcrumbs=["Home", "Dashboard"],
        subtitle="Organization overview and real-time business intelligence",
        icon="📊",
    )

    user = st.session_state.get("if_user_name", "Alex")
    org = st.session_state.get("if_org_name", "Acme Corporation")
    role = st.session_state.get("if_user_role", "Admin")
    role_group = st.session_state.get("if_user_role_group", "General")
    dashboard_context = get_dashboard_context(role)

    hero_actions = {
        "Data Analyst": [("Review data quality", "shield-check"), ("Explore trends", "bar-chart-3"), ("Generate report", "file-text")],
        "Data Scientist": [("Inspect models", "brain"), ("Review features", "layers"), ("Plan experiment", "sparkles")],
        "Manager": [("Check delivery", "calendar"), ("Review team pulse", "users"), ("Share update", "megaphone")],
        "Admin": [("Audit access", "shield"), ("Review governance", "settings"), ("Check health", "activity")],
    }
    
    @st.dialog("Edit Profile & Role")
    def edit_profile_dialog():
        from utils.helpers import get_homepage_role_options, set_homepage_role_selection
        role_options = get_homepage_role_options()
        role_labels = [f"{r} ({g})" for g, opts in role_options.items() for r in opts]
        
        current_role = st.session_state.get("if_user_role", "Admin")
        default_idx = 0
        for i, label in enumerate(role_labels):
            if label.startswith(current_role):
                default_idx = i
                break
                
        selected_label = st.selectbox("User role", options=role_labels, index=default_idx)
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Full name", value=st.session_state.get("if_user_name", "Alex Morgan"))
            email = st.text_input("Email address", value=st.session_state.get("if_user_email", "alex.morgan@acmecorp.com"))
            phone = st.text_input("Phone number", value=st.session_state.get("if_user_phone", ""))
        with c2:
            company = st.text_input("Company", value=st.session_state.get("if_org_name", "Acme Corporation"))
            password = st.text_input("Password", type="password", value=st.session_state.get("if_user_password", ""))
            department = st.text_input("Department", value=st.session_state.get("if_user_department", "Data & Analytics"))
            
        if st.button("Save Changes", type="primary", use_container_width=True):
            if selected_label:
                chosen_role = selected_label.split(" (")[0]
                set_homepage_role_selection(chosen_role)
            st.session_state["if_user_name"] = full_name
            st.session_state["if_user_email"] = email
            st.session_state["if_user_phone"] = phone
            st.session_state["if_org_name"] = company
            st.session_state["if_user_password"] = password
            st.session_state["if_user_department"] = department
            st.success("Profile updated successfully!")
            st.rerun()

    # ── #15 Comparison Mode ────────────────────────────────────────────────
    with st.expander("⚖️ Period Comparison Mode", expanded=False):
        cm1, cm2, cm3 = st.columns([1, 1, 0.5])
        with cm1:
            period_a = st.selectbox("Period A", ["This Month", "Last Month", "Q3 2024", "Q2 2024", "Last 7 Days"], key="cmp_period_a")
        with cm2:
            period_b = st.selectbox("Period B", ["Last Month", "This Month", "Q2 2024", "Q1 2024", "Prev 7 Days"], key="cmp_period_b")
        with cm3:
            compare_on = st.button("Compare", type="primary", use_container_width=True, key="cmp_btn")
        if compare_on or st.session_state.get("cmp_active"):
            st.session_state["cmp_active"] = True
            import random
            diffs = {
                "Footfall":  (random.randint(18000, 32000), random.randint(14000, 28000)),
                "Revenue":   (random.randint(420, 680),     random.randint(380, 620)),
                "Tenants":   (247, 241),
                "Satisfaction": (4.6, 4.3),
            }
            st.html('<div class="if-compare-banner" style="flex-wrap:wrap;gap:8px;">' +
                f'<span class="if-compare-chip">{period_a}</span>' +
                '<span class="if-compare-vs"> vs </span>' +
                f'<span class="if-compare-chip" style="background:#2563eb;">{period_b}</span>' +
                '&nbsp;&nbsp;' +
                ''.join([
                    f'<span style="font-size:12px;padding:3px 10px;border-radius:20px;'
                    f'background:{"rgba(16,185,129,0.1)" if b[0]>=b[1] else "rgba(239,68,68,0.1)"};'
                    f'color:{"#10b981" if b[0]>=b[1] else "#ef4444"};font-weight:600;">'
                    f'{k}: {b[0]:,} {"▲" if b[0]>=b[1] else "▼"} vs {b[1]:,}</span>'
                    for k, b in diffs.items()
                ]) +
                '</div>', )
            if st.button("✕ Clear comparison", key="cmp_clear"):
                st.session_state["cmp_active"] = False
                st.rerun()
    # ──────────────────────────────────────────────────────────────────────

    c1, c2 = st.columns([0.8, 0.2])
    with c1:
        hero_section(
            f"Welcome back, {user.split()[0]} 👋",
            f"{org} registered 2.48M visitors this month, with 3 new high-priority tenant lease renewals and 2 accounts flagged for churn intervention. {dashboard_context['hero_copy']} You are currently viewing the workspace as a {role} in {role_group}.",
            hero_actions.get(role, [("Run AI Analysis", "sparkles"), ("Open Executive Dashboard", "bar-chart-3"), ("Generate Report", "file-text")]),
        )
    with c2:
        st.write("")
        st.write("")
        if st.button("⚙️ Edit Profile & Role", use_container_width=True):
            edit_profile_dialog()

    for alert in get_alerts(role):
        alert_banner(alert["level"], alert["title"], alert["message"])

    render_command_center()

    st.markdown('<div class="if-section"><div class="if-section-title">Business Pulse</div></div>', unsafe_allow_html=True)
    render_hero_os()

    section_header(dashboard_context["kpi_title"], f"A {dashboard_context['focus'].lower()}-focused view of the signals that matter most")
    metric_grid(get_kpis(role), columns=4)

    st.markdown(
        '<div class="if-card" style="margin: 18px 0 16px; padding: 18px 20px;">'
        '<div class="if-card-header">'
        '<div><div class="if-card-title">Daily Brief</div><div class="if-card-subtitle">A focused view of today’s mall operations.</div></div>'
        '<span class="if-badge primary">Priority</span>'
        '</div>'
        '<div class="if-stat-strip">'
        '<span class="if-badge success">Security staffing at 100%</span>'
        '<span class="if-badge warning">HVAC in Food Court needs attention</span>'
        '<span class="if-badge neutral">All anchor stores opened on time</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    render_insight_stories()
    render_charts(role)
    render_recommendations_tasks(role)
    render_activity_reports()

    st.html(
        """
    <div class="if-footer-bar">
        <div class="if-footer-item"><strong>Version</strong> 1.0.0</div>
        <div class="if-footer-item"><strong>API Status</strong> Healthy</div>
        <div class="if-footer-item"><strong>AI Status</strong> Online</div>
        <div class="if-footer-item"><strong>Database</strong> Connected</div>
        <div class="if-footer-item"><strong>Latency</strong> 42 ms</div>
        <div class="if-footer-item"><strong>Jobs Running</strong> 7</div>
    </div>
    """
    )

    finish_page()


main()
