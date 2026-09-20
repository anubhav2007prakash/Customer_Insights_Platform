"""Predictions — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.charts.chart_factory import bar_chart, gauge_chart, scatter_chart
from components.ui.cards import alert_banner, hero_section, metric_grid, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_predictions


def render_churn_table(pred) -> None:
    """Render the main predictions table and risk gauge."""
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        st.dataframe(
            pred,
            use_container_width=True,
            hide_index=True,
            column_config={
                "churn_prob": st.column_config.ProgressColumn("Churn Prob.", format="%.0f%%", min_value=0.0, max_value=1.0),
                "clv": st.column_config.NumberColumn("CLV", format="$%d"),
            },
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        gauge_chart(21, "Portfolio Churn Risk Index", 100)
        st.markdown("</div>", unsafe_allow_html=True)


def render_risk_analysis(pred) -> None:
    """Render risk analytics charts."""
    section_header("Risk analysis", "Patterns and clusters supporting the prediction")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        bar_chart(pred, "customer", "churn_prob", "Churn Probability by Account", horizontal=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        scatter_chart(pred, "clv", "churn_prob", "risk", "segment", 360)
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Bootstrap and render Predictions page."""
    bootstrap_page(
        "Predictions",
        "predictions",
        breadcrumbs=["AI", "Predictions"],
        subtitle="ML-powered churn, CLV, and customer health predictions",
        icon="🎯",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    hero_copy = {
        "Data Analyst": "The prediction workspace highlights the accounts most likely to churn and the signals that deserve deeper analysis.",
        "Data Scientist": "The prediction workspace highlights the accounts most likely to churn and the feature patterns behind the strongest signals.",
        "Manager": "The prediction workspace highlights the accounts most likely to churn and the actions that minimize risk quickly.",
        "Admin": "The prediction workspace highlights the accounts most likely to churn and the control checks that keep the risk model safe.",
    }

    hero_section(
        f"{dashboard_context['hero_title']} — predictions",
        hero_copy.get(role, "The platform is now highlighting the accounts most likely to churn and the customers with the highest upside."),
        [("Review risk signals", "target"), ("Open action queue", "alert-triangle")],
    )

    # Actionable options
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Run Batch Prediction Simulation", type="primary", use_container_width=True):
            st.session_state["predictions_simulated"] = True
            st.success("Successfully recalculated prediction models. Fresh CLV and Churn metrics loaded.")
    with c2:
        if st.button("Export Risk Watchlist", use_container_width=True):
            st.info("Downloading risk watchlist...")

    if st.session_state.get("predictions_simulated"):
        alert_banner("success", "Simulation finished", "Batch predictions simulated successfully with fresh data inputs.")
    else:
        alert_banner("warning", "Risk attention needed", "A small cluster of accounts now warrants immediate intervention based on recent engagement decline.")

    metric_grid([
        {"label": "Churn Risk (30d)", "value": "2.1%", "change": -0.4, "icon": "activity", "tone": "danger"},
        {"label": "High-Risk Accounts", "value": "142", "change": -8.5, "icon": "alert-triangle", "tone": "warning"},
        {"label": "Model AUC", "value": "0.94", "change": 1.2, "icon": "target", "tone": "success"},
        {"label": "Predictions Run", "value": "48K", "change": 12.0, "icon": "cpu", "tone": "primary"},
    ], columns=4)

    # ML Model Configuration Options
    with st.expander("⚙️ AI Model Parameters & Risk Threshold Tuning", expanded=True):
        st.markdown("<div style='font-size:13px; color:#4b5563; margin-bottom:10px;'>Adjust risk cutoffs, discount rates, and sensitivity parameters for real-time model inference tuning.</div>", unsafe_allow_html=True)
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            high_risk_cutoff = st.slider("High Risk Cutoff (%)", min_value=50, max_value=90, value=70, step=5, key="pred_high_cutoff") / 100.0
        with mc2:
            med_risk_cutoff = st.slider("Medium Risk Cutoff (%)", min_value=20, max_value=50, value=40, step=5, key="pred_med_cutoff") / 100.0
        with mc3:
            clv_discount_rate = st.slider("CLV Discount Rate (%)", min_value=1.0, max_value=20.0, value=8.5, step=0.5, key="pred_clv_discount") / 100.0

        if st.button("Apply Model Controls & Recalculate Risk", type="primary"):
            st.session_state["if_custom_model_params"] = True
            st.success(f"Model parameters applied: High Cutoff={high_risk_cutoff*100:.0f}%, Medium Cutoff={med_risk_cutoff*100:.0f}%, Discount Rate={clv_discount_rate*100:.1f}%.")

    pred = get_predictions()
    if "churn_prob" in pred.columns:
        pred["risk"] = pred["churn_prob"].apply(
            lambda p: "High" if p >= high_risk_cutoff else ("Medium" if p >= med_risk_cutoff else "Low")
        )

    section_header("Churn predictions", "The most likely churn cases by account with active threshold filters")
    render_churn_table(pred)
    render_risk_analysis(pred)

    from utils.report_export import render_export_ui
    with st.expander("📥 Export Watchlist & Prediction Results", expanded=False):
        render_export_ui(pred, filename_prefix="churn_predictions_watchlist", title="Customer Churn Risk Watchlist", key_prefix="pred_exp")

    finish_page()


main()

