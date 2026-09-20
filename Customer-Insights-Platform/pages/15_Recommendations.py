"""Tenant Cross-Promotion AI — OmniMall AI."""

from __future__ import annotations

import streamlit as st

from components.ui.cards import alert_banner, hero_section, metric_grid, progress_bar, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page


def render_priority_actions() -> None:
    """Render priority cross-promotion actions."""
    section_header("Active Cross-Promotions", "The highest-value tenant pairing offers currently active in the loyalty app and concierge")
    recs = [
        {"action": "Offer 15% Coffee Discount to Cinema Buyers", "impact": "High", "segment": "AMC Theatres → Starbucks"},
        {"action": "Bundle Apple Care+ with iPhone Purchase at Apple Store", "impact": "High", "segment": "Apple Store → Service Desk"},
        {"action": "Complimentary Fitting Room at Zara for Sephora Loyalty Members", "impact": "Medium", "segment": "Sephora → Zara"},
        {"action": "10% Off H&M for Food Court Visitors > $30 Spend", "impact": "Medium", "segment": "Food Court → H&M"},
        {"action": "Earn 2× Points at Starbucks after Gym Visit", "impact": "Low", "segment": "Fitness Center → Starbucks"},
    ]

    for i, rec in enumerate(recs):
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"**{rec['action']}**")
                st.markdown(f"<span class='if-caption'>Pairing: {rec['segment']}</span>", unsafe_allow_html=True)
            with c2:
                tone = "danger" if rec["impact"] == "High" else "warning" if rec["impact"] == "Medium" else "success"
                st.markdown(f"<span class='if-badge {tone}'>{rec['impact']} Value</span>", unsafe_allow_html=True)
            with c3:
                key = f"apply_reco_{i}"
                if st.button("Push to App", key=key, type="primary"):
                    st.session_state[f"reco_applied_{i}"] = True
                    st.rerun()

            if st.session_state.get(f"reco_applied_{i}"):
                st.success(f"✅ **{rec['action']}** is now live in the Mall Loyalty App and Concierge kiosks.")

            progress_bar(68 + i * 4, f"AI Confidence: {68 + i * 4}%")
            st.markdown("---")


def render_tenant_suggestions() -> None:
    """Render AI-generated tenant cross-referral suggestions."""
    section_header("AI Tenant Pairing Engine", "The engine automatically identifies high-conversion tenant pairs based on shopping patterns")
    pairings = [
        ("AMC Theatres + Starbucks", "Cinema-goers spend 40% more at F&B post-film", "44% success rate", 91),
        ("Apple Store + Tech Accessories Kiosk", "iPhone buyers have 38% cross-shop rate for accessories", "38% success rate", 84),
        ("Sephora + Zara", "Beauty shoppers convert to fashion 28% of the time", "28% success rate", 76),
        ("Nike Flagship + Fitness Center", "Athletic footwear buyers enroll in gym promos 22% of the time", "22% success rate", 68),
    ]
    for pair, insight, conv, conf in pairings:
        st.markdown('<div class="if-card" style="margin-bottom:12px">', unsafe_allow_html=True)
        st.markdown(f"**{pair}**")
        st.markdown(f"<span class='if-caption'>{insight} · {conv}</span>", unsafe_allow_html=True)
        progress_bar(conf, f"Confidence {conf}%")
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Bootstrap and render Cross-Promotion AI page."""
    bootstrap_page(
        "Cross-Promotion AI",
        "recommendations",
        breadcrumbs=["Marketing & Loyalty", "Cross-Promotion AI"],
        subtitle="AI-driven tenant cross-referral campaigns and loyalty app push notifications",
        icon="⚡",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)

    hero_section(
        "Tenant Cross-Promotion AI",
        "Maximize mall revenue per visitor by dynamically generating tenant pairing suggestions and loyalty program incentives tailored to each shopper's behaviour across the mall.",
        [("Review Live Promotions", "zap"), ("Generate New Pairings", "layers")],
    )

    alert_banner("success", "Cross-promo engine is active", "The loyalty app and concierge kiosks are receiving real-time pairing suggestions for Cinema and Food & Bev tenants.")

    metric_grid([
        {"label": "Avg Cross-Shop Rate", "value": "22.4%", "change": 3.1, "icon": "shuffle", "tone": "primary"},
        {"label": "Promo Redemption Rate", "value": "64%", "change": 5.1, "icon": "check-circle", "tone": "success"},
        {"label": "Cross-Promo Revenue YTD", "value": "$1.42M", "change": 22.0, "icon": "dollar-sign", "tone": "accent"},
        {"label": "Active Pairings", "value": "18", "change": 4.0, "icon": "link", "tone": "warning"},
    ], columns=4)

    # Recommendation Engine Model Options
    with st.expander("🎛️ Recommendation Engine Algorithm Weights & Options", expanded=True):
        st.markdown("<div style='font-size:13px; color:#4b5563; margin-bottom:10px;'>Fine-tune the weight matrix used for tenant pairing recommendations.</div>", unsafe_allow_html=True)
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            w_collab = st.slider("Collaborative Filtering Weight", 0, 100, 50, key="reco_w_collab")
        with rc2:
            w_content = st.slider("Content Affinity Weight", 0, 100, 30, key="reco_w_content")
        with rc3:
            w_trending = st.slider("Trending Boost Weight", 0, 100, 20, key="reco_w_trending")

        if st.button("Re-weight Recommendation Engine", type="primary"):
            st.session_state["reco_weights"] = {"collab": w_collab, "content": w_content, "trending": w_trending}
            st.success(f"Recommendation engine updated with weights: Collab={w_collab}%, Content={w_content}%, Trending={w_trending}%.")

    render_priority_actions()
    render_tenant_suggestions()

    finish_page()


main()

