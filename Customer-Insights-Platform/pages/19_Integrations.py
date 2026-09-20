"""Integrations — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.ui.cards import section_header, status_indicator
from utils.helpers import get_dashboard_context, relative_time
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_integrations


def render_sync_metrics() -> None:
    """Render high level synchronization status metrics."""
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Connected", "5")
    with c2:
        st.metric("Available", "12")
    with c3:
        st.metric("Last Sync", "2h ago")


def render_integration_catalog() -> None:
    """Render details of available integration services."""
    section_header("Integration Catalog")
    df = get_integrations()
    for i, row in df.iterrows():
        # Check if connected
        is_connected = row["status"] == "Connected" or st.session_state.get(f"if_integration_conn_{row['name']}", False)
        status = "online" if is_connected else "pending"
        status_label = "Connected" if is_connected else "Available"
        sync = relative_time(row["last_sync"]) if is_connected else "—"

        st.markdown(
            f"""
            <div class="if-card" style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <div style="font-weight:600;font-size:15px">{row['name']}</div>
                        <div class="if-caption">{row['category']} · Last sync: {sync}</div>
                    </div>
                    <span class="if-badge {'success' if is_connected else 'neutral'}">{status_label}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not is_connected:
            if st.button(f"Connect {row['name']}", key=f"conn_{row['name']}_{i}"):
                st.session_state[f"if_integration_conn_{row['name']}"] = True
                st.success(f"Integration with **{row['name']}** established successfully.")
                st.rerun()


def render_webhook_configurator() -> None:
    """#20 Webhook Configurator — full CRUD-style webhook manager."""
    section_header("🔗 Webhook Configurator", "Push real-time events to Slack, Teams, or any HTTP endpoint")

    # Existing webhooks
    webhooks = [
        {"name": "Slack Alerts",     "url": "https://hooks.slack.com/services/T00/B00/xxx", "event": "anomaly.detected",  "status": "active",   "deliveries": 1284},
        {"name": "Teams Notifier",   "url": "https://outlook.office.com/webhook/xxx",        "event": "report.generated", "status": "active",   "deliveries": 342},
        {"name": "CRM Sync",         "url": "https://api.salesforce.com/webhook/v2/xxx",     "event": "tenant.updated",   "status": "paused",   "deliveries": 89},
        {"name": "PagerDuty",        "url": "https://events.pagerduty.com/v2/enqueue",       "event": "alert.critical",   "status": "active",   "deliveries": 17},
    ]
    for w in webhooks:
        status_color = "#10b981" if w["status"] == "active" else "#f59e0b"
        st.html(f"""
        <div class="if-webhook-row">
          <div>
            <div style="font-size:13px;font-weight:600;color:#0f1028;">{w['name']}</div>
            <div class="if-webhook-event">{w['event']}</div>
          </div>
          <div class="if-webhook-url">{w['url']}</div>
          <span style="font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;
            background:{'rgba(16,185,129,0.1)' if w['status']=='active' else 'rgba(245,158,11,0.1)'};
            color:{status_color};">{w['status'].upper()}</span>
          <span style="font-size:11px;color:#6b7280;">{w['deliveries']:,} sent</span>
        </div>""")

    st.divider()

    with st.expander("➕ Add New Webhook", expanded=False):
        with st.form("webhook_add_form"):
            wc1, wc2 = st.columns(2)
            with wc1:
                w_name = st.text_input("Webhook name", placeholder="e.g. Slack Ops Channel")
                w_url = st.text_input("Endpoint URL", placeholder="https://hooks.slack.com/…")
                w_secret = st.text_input("Signing secret", type="password", placeholder="whsec_…")
            with wc2:
                w_event = st.multiselect("Events to subscribe", [
                    "anomaly.detected", "report.generated", "tenant.updated",
                    "lease.expiring", "alert.critical", "footfall.spike",
                    "user.login", "export.completed",
                ], default=["anomaly.detected"])
                w_retries = st.number_input("Max retries", min_value=0, max_value=5, value=3)
                w_timeout = st.number_input("Timeout (seconds)", min_value=5, max_value=30, value=10)
            sub = st.form_submit_button("Register Webhook", type="primary", use_container_width=True)
            if sub:
                if w_name and w_url:
                    st.success(f"✅ Webhook **{w_name}** registered for {len(w_event)} event(s).")
                else:
                    st.error("Name and URL are required.")


def main() -> None:
    """Bootstrap and render Integrations page."""
    bootstrap_page(
        "Integrations",
        "integrations",
        breadcrumbs=["Data", "Integrations"],
        subtitle="Connect CRM, e-commerce, payments, and analytics platforms",
        icon="🔌",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    section_header(f"{dashboard_context['hero_title']} — integrations")

    tab1, tab2 = st.tabs(["🔌 Integration Catalog", "🔗 Webhooks"])
    with tab1:
        render_sync_metrics()
        render_integration_catalog()
    with tab2:
        render_webhook_configurator()

    finish_page()


main()
