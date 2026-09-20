"""AI Center — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.ui.cards import action_prompt_chips, alert_banner, chat_interface, hero_section, insight_card, metric_grid, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_ai_insights, get_ai_suggestions, get_chat_history


def render_chat_column(role: str) -> None:
    """Render the AI assistant chat column."""
    section_header("AI assistant", "Ask the platform for guidance, summaries, and next steps")
    action_prompt_chips(get_ai_suggestions(role))
    chat_interface(get_chat_history(), get_ai_suggestions(role))
    prompt = st.chat_input("Ask anything about your business data…")
    if prompt:
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write(
            f"Based on your data, here's my analysis of **{prompt}**: "
            "Enterprise segment revenue grew 12.4% this period, driven primarily by upsells "
            "in Analytics Pro and AI Insights. Would you like a detailed breakdown?"
        )


def render_config_column(role: str) -> None:
    """Render the model selector and insights column."""
    section_header("Model selector", "Tune the reasoning profile for the moment")
    st.html(
        """
        <div class="if-story-card if-fade-in">
            <div class="if-story-head">
                <div class="if-story-title">Active configuration</div>
                <span class="if-badge primary">Balanced</span>
            </div>
            <div class="if-story-copy">The current setup favors high-confidence recommendations with low latency for live business teams.</div>
        </div>
        """
    )
    model_options = ["InsightForge GPT-4o", "InsightForge Analyst", "InsightForge Forecaster"]
    current_model = st.session_state.get("if_ai_model", "InsightForge GPT-4o")
    model = st.selectbox(
        "Active model",
        model_options,
        index=model_options.index(current_model) if current_model in model_options else 0,
    )
    temperature = st.slider("Temperature", 0.0, 1.0, float(st.session_state.get("if_ai_temperature", 0.3)))
    st.progress(0.72, text="Token budget: 72% used")

    if st.button("Apply Model Settings", type="primary", use_container_width=True):
        st.session_state["if_ai_model"] = model
        st.session_state["if_ai_temperature"] = temperature
        st.success(f"Model set to **{model}** with temperature {temperature:.1f}.")

    section_header("Recent insights", "Most relevant prompts surfaced this week")
    for ins in get_ai_insights(role):
        insight_card(ins["title"], ins["body"])

    section_header("AI recommendations", "Ready to act on now")
    for rec in get_ai_suggestions(role):
        st.markdown(f"→ {rec}")

    # ── #4 AI Anomaly Feed ────────────────────────────────────────────────────
    section_header("🔍 Anomaly Feed", "AI-detected data anomalies requiring attention")
    anomalies = [
        {"title": "Footfall spike — North Wing", "sev": "critical", "body": "Footfall 340% above baseline at 2:14 PM. Possible event collision or sensor error. Cross-check CCTV feed.", "time": "8 min ago", "icon": "🚨"},
        {"title": "Revenue drop — Food Court 2", "sev": "warning",  "body": "Sales 28% below 7-day average for last 3 hours. 4 stalls reported POS issues. Maintenance dispatched.", "time": "22 min ago", "icon": "⚠️"},
        {"title": "Parking utilization ceiling", "sev": "warning",  "body": "Garage B at 94% capacity — 18% above Friday average. Dynamic wayfinding signage updated automatically.", "time": "1 hr ago", "icon": "🅿️"},
        {"title": "New loyalty cohort detected",  "sev": "info",    "body": "AI identified a new high-value segment: 1,240 visitors aged 28–34 with 3× loyalty point accumulation rate.", "time": "3 hr ago", "icon": "✨"},
    ]
    for a in anomalies:
        col_a, col_b = st.columns([5, 1])
        with col_a:
            st.html(f"""
            <div class="if-anomaly-card {a['sev']}">
              <div class="if-anomaly-header">
                <span style="font-size:16px;">{a['icon']}</span>
                <span class="if-anomaly-title">{a['title']}</span>
                <span class="if-anomaly-sev {a['sev']}">{a['sev'].upper()}</span>
              </div>
              <div class="if-anomaly-body">{a['body']}</div>
              <div class="if-anomaly-footer">
                <span class="if-anomaly-meta">🕐 {a['time']}</span>
              </div>
            </div>""")
        with col_b:
            st.button("Investigate", key=f"inv_{a['title'][:12]}", use_container_width=True)
    # ─────────────────────────────────────────────────────────────────────────


def main() -> None:
    """Bootstrap and render the AI Center page."""
    bootstrap_page(
        "AI Center",
        "ai_center",
        breadcrumbs=["AI", "AI Center"],
        subtitle="Your intelligent command center for data-driven decisions",
        icon="✨",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    hero_copy = {
        "Data Analyst": "This workspace surfaces quality monitors, anomaly signals, and next-step recommendations for fast, trustworthy analysis.",
        "Data Scientist": "This workspace surfaces model readiness, experiment signals, and feature guidance for stronger predictive outcomes.",
        "Manager": "This workspace surfaces delivery signals, team priorities, and leadership-ready next actions.",
        "Admin": "This workspace surfaces platform health, governance posture, and operational readiness for safe rollout.",
    }

    hero_section(
        f"{dashboard_context['hero_title']} — AI",
        hero_copy.get(role, "This workspace brings forecasting, recommendations, and model guidance together so the next action is always obvious."),
        [("Invoke analyst", "sparkles"), ("Open playbooks", "layers")],
    )

    alert_banner("info", "Models healthy", "The active orchestration stack is stable and producing fresh recommendations every few minutes.")

    metric_grid([
        {"label": "Insights Generated", "value": "1,284", "change": 22.4, "icon": "sparkles", "tone": "primary"},
        {"label": "Queries Today", "value": "847", "change": 15.2, "icon": "message-square", "tone": "accent"},
        {"label": "Model Accuracy", "value": "94.2%", "change": 1.8, "icon": "target", "tone": "success"},
        {"label": "Token Usage", "value": "2.4M", "change": 8.1, "icon": "cpu", "tone": "warning"},
    ], columns=4)

    c1, c2 = st.columns([2, 1])
    with c1:
        render_chat_column(role)
    with c2:
        render_config_column(role)

    finish_page()


main()
