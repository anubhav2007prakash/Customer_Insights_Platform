"""Footfall & Event Forecasting — OmniMall AI."""

from __future__ import annotations

import streamlit as st

from components.charts.chart_factory import forecast_chart, multi_line_chart
from components.ui.cards import alert_banner, hero_section, metric_grid, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_alerts, get_forecast_series, get_revenue_trend


def render_scenario_analysis() -> None:
    """Render scenario comparison section."""
    section_header("Holiday & Event Scenario Comparison", "Compare optimistic, baseline, and downside footfall projections for mall events")
    rev = get_revenue_trend(30)
    rev["optimistic"] = rev["footfall"] * 1.35
    rev["pessimistic"] = rev["footfall"] * 0.75
    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    multi_line_chart(rev, "date", ["footfall", "optimistic", "pessimistic"], "Footfall Scenario Analysis")
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Bootstrap and render Forecasting page."""
    bootstrap_page(
        "Event Forecasting",
        "forecasting",
        breadcrumbs=["Marketing & Loyalty", "Event Forecasting"],
        subtitle="Predict holiday mall footfall, parking utilization, and event attendance with AI",
        icon="📉",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)

    hero_section(
        "AI Footfall & Event Forecasting",
        "Anticipate visitor volumes ahead of major holidays, anchor-store openings, and mall events like Black Friday to ensure optimal staffing, parking, and tenant readiness.",
        [("Run Holiday Scenario", "trending-up"), ("Export Event Plan", "download")],
    )

    alert_banner("warning", "High Footfall Risk Detected", "The AI predicts Parking Garage A will be at 98% capacity 3 days before the Black Friday weekend.")

    # Active selections
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        zone = st.selectbox("Zone to Forecast", ["Mall-Wide", "North Wing", "South Wing", "Food Court", "Atrium", "Parking Garages"], key="forecast_zone")
    with fc2:
        model = st.selectbox("AI Model", ["Seasonal Ensemble (Recommended)", "ARIMA Time Series", "Neural Prophet"], key="forecast_model")
    with fc3:
        horizon = st.selectbox("Horizon", ["30 days", "90 days", "Black Friday Prep", "Holiday Season (Dec)"], key="forecast_horizon")

    if st.button("Generate Footfall Forecast", type="primary", use_container_width=True):
        st.session_state["forecast_configured"] = True
        st.success(f"Forecasting profile updated for **{zone}** using **{model}** model over **{horizon}** horizon.")

    metric_grid([
        {"label": f"Projected Footfall ({zone})", "value": "164,200", "change": 18.0, "icon": "trending-up", "tone": "primary"},
        {"label": "Prediction Confidence", "value": "96%", "change": 2.1, "icon": "target", "tone": "success"},
        {"label": "Suggested Extra Staff", "value": "+82", "change": 0.8, "icon": "users", "tone": "accent"},
        {"label": "Peak Day Forecast", "value": "Nov 29", "change": 0, "icon": "calendar", "tone": "danger"},
    ], columns=4)

    section_header(f"{zone} Footfall Forecast", f"Expected daily footfall and confidence interval for {zone.lower()}")
    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    forecast_chart(get_forecast_series(), "month", "value", "lower", "upper")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── #13 Confidence Intervals ─────────────────────────────────────────────
    section_header("Forecast Confidence Intervals", "Uncertainty bands show where 80% of actual outcomes are expected to land")
    import plotly.graph_objects as go
    import pandas as pd
    import numpy as np
    fc = get_forecast_series()
    periods = list(range(len(fc)))
    base = fc["value"].values
    upper80 = fc["upper"].values
    lower80 = fc["lower"].values
    upper95 = base + (upper80 - base) * 1.45
    lower95 = base - (base - lower80) * 1.45

    fig_ci = go.Figure()
    fig_ci.add_trace(go.Scatter(
        x=list(fc["month"]) + list(fc["month"])[::-1],
        y=list(upper95) + list(lower95)[::-1],
        fill="toself", fillcolor="rgba(99,102,241,0.08)",
        line=dict(color="rgba(0,0,0,0)"), name="95% CI", showlegend=True,
    ))
    fig_ci.add_trace(go.Scatter(
        x=list(fc["month"]) + list(fc["month"])[::-1],
        y=list(upper80) + list(lower80)[::-1],
        fill="toself", fillcolor="rgba(99,102,241,0.18)",
        line=dict(color="rgba(0,0,0,0)"), name="80% CI", showlegend=True,
    ))
    fig_ci.add_trace(go.Scatter(
        x=fc["month"], y=base, mode="lines+markers",
        line=dict(color="#6366f1", width=2.5), name="Forecast",
        marker=dict(size=5, color="#6366f1"),
    ))
    fig_ci.update_layout(
        title="Footfall Forecast with Confidence Bands",
        xaxis_title="Month", yaxis_title="Footfall",
        height=340, margin=dict(l=40, r=20, t=44, b=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        font=dict(family="Plus Jakarta Sans", size=12),
    )
    st.plotly_chart(fig_ci, use_container_width=True)

    ci_c1, ci_c2, ci_c3 = st.columns(3)
    ci_c1.html('<div class="if-anomaly-card info"><div class="if-anomaly-header">'
               '<span class="if-anomaly-title">📊 80% Confidence Band</span></div>'
               '<div class="if-anomaly-body">80% of actual footfall values are expected to fall within the shaded inner band based on 24 months of historical variance.</div></div>')
    ci_c2.html('<div class="if-anomaly-card warning"><div class="if-anomaly-header">'
               '<span class="if-anomaly-title">⚠️ Model Uncertainty</span></div>'
               '<div class="if-anomaly-body">Wider bands indicate higher uncertainty — typically around public holidays and novel mall events with limited historical data.</div></div>')
    ci_c3.html('<div class="if-anomaly-card info"><div class="if-anomaly-header">'
               '<span class="if-anomaly-title">🎯 95% Outer Band</span></div>'
               '<div class="if-anomaly-body">Extreme footfall events (weather disruptions, viral promotions) fall in the outer 95% band. Staff contingency plans should cover this range.</div></div>')
    # ─────────────────────────────────────────────────────────────────────────

    finish_page()


main()
