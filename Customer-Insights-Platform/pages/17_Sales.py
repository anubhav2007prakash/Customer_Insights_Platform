"""Mall Concierge Desk — OmniMall AI."""

from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import datetime

from components.ui.cards import alert_banner, hero_section, metric_grid, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page


def init_concierge_state():
    """Initialize Concierge session state variables."""
    if "concierge_cart" not in st.session_state:
        st.session_state["concierge_cart"] = []
    if "concierge_transactions" not in st.session_state:
        st.session_state["concierge_transactions"] = [
            {"Time": "10:42 AM", "Service": "Gift Card – $100", "Method": "Card"},
            {"Time": "10:28 AM", "Service": "Stroller Rental", "Method": "Cash"},
            {"Time": "10:15 AM", "Service": "Wheelchair Rental", "Method": "App Pay"},
            {"Time": "09:41 AM", "Service": "Gift Card – $250", "Method": "Card"},
        ]
    if "concierge_daily_revenue" not in st.session_state:
        st.session_state["concierge_daily_revenue"] = 3820.0
    if "concierge_daily_tx" not in st.session_state:
        st.session_state["concierge_daily_tx"] = 28


def render_concierge_desk() -> None:
    """Render the Concierge Desk service form."""
    section_header("Concierge Services", "Issue Gift Cards, Rentals, and Lost & Found services")

    c1, c2 = st.columns([1.8, 1.2])
    with c1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        st.subheader("Request a Service")

        item_col, qty_col = st.columns([3, 1])
        with item_col:
            service = st.selectbox(
                "Select Service",
                [
                    "Mall Gift Card – $25",
                    "Mall Gift Card – $50",
                    "Mall Gift Card – $100",
                    "Mall Gift Card – $250",
                    "Stroller Rental – $5/hr",
                    "Wheelchair Rental – Free",
                    "Luggage Locker – $3/hr",
                    "Lost & Found Report",
                    "Directions / Map",
                ]
            )
        with qty_col:
            qty = st.number_input("Qty", min_value=1, value=1, step=1)

        notes = st.text_input("Notes / Guest Name", placeholder="Optional...")
        payment_method = st.selectbox("Payment Method", ["Credit Card", "Cash", "Mall App Pay", "Debit Card"])

        col_checkout, col_void = st.columns(2)
        with col_checkout:
            if st.button("Process Request", type="primary", use_container_width=True):
                # Parse price
                price_str = service.split("$")[-1].split("/")[0].replace(",", "") if "$" in service else "0"
                try:
                    price = float(price_str) * qty
                except ValueError:
                    price = 0.0

                st.session_state["concierge_transactions"].insert(0, {
                    "Time": datetime.now().strftime("%I:%M %p"),
                    "Service": service,
                    "Method": payment_method,
                })
                st.session_state["concierge_daily_revenue"] += price
                st.session_state["concierge_daily_tx"] += 1

                st.success(f"✅ **{service}** processed for guest{' — ' + notes if notes else ''}. Total: **${price:,.2f}**.")

        with col_void:
            if st.button("Cancel / Void", type="secondary", use_container_width=True):
                st.info("Last transaction flagged for supervisor review.")

        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="if-card" style="height: 100%;">', unsafe_allow_html=True)
        st.subheader("Today's Service Log")
        recent_df = pd.DataFrame(st.session_state["concierge_transactions"][:8])
        st.dataframe(recent_df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Kiosk Map Lookup")
        st.selectbox("Find a Store or Facility", [
            "Apple Store – North Wing L1",
            "Zara – South Wing L1",
            "AMC Theatres – Atrium L3",
            "Starbucks – North Wing L1",
            "Restrooms – All Wings",
            "Parking – Garage A & B",
            "ATM – Near Food Court",
            "Security Office – Ground Floor",
        ], key="concierge_lookup")
        st.markdown('</div>', unsafe_allow_html=True)


def render_concierge_metrics() -> None:
    """Render daily concierge desk metrics."""
    section_header("Today's Concierge Activity", "Live view of current shift performance at the concierge desk")

    daily_rev = st.session_state.get("concierge_daily_revenue", 3820.0)
    tx_count = st.session_state.get("concierge_daily_tx", 28)

    metric_grid([
        {"label": "Gift Cards Issued", "value": f"${daily_rev:,.0f}", "change": 6.2, "icon": "gift", "tone": "primary"},
        {"label": "Stroller/Wheelchair Rentals", "value": "14", "change": 2.0, "icon": "accessibility", "tone": "success"},
        {"label": "Requests Handled", "value": str(tx_count), "change": 8.1, "icon": "clipboard-list", "tone": "accent"},
        {"label": "Guest Satisfaction", "value": "4.8 / 5", "change": 0.2, "icon": "star", "tone": "warning"},
    ], columns=4)


def main() -> None:
    """Bootstrap and render Concierge Desk page."""
    init_concierge_state()

    bootstrap_page(
        "Concierge Desk",
        "sales",
        breadcrumbs=["Tenant Management", "Concierge Desk"],
        subtitle="Issue gift cards, manage visitor rentals, and handle Lost & Found",
        icon="🛎️",
    )

    role = st.session_state.get("if_user_role", "Admin")

    hero_section(
        "Mall Concierge Desk",
        "The Concierge Desk handles visitor services including universal Mall Gift Cards, stroller and wheelchair rentals, lost & found, and in-mall navigation assistance.",
        [("View Mall Map", "map"), ("Print Gift Card Batch", "printer")],
    )

    alert_banner("success", "Desk Open", "The concierge desk is online and connected to the central visitor services system.")

    render_concierge_metrics()
    st.write("")
    render_concierge_desk()

    finish_page()


main()
