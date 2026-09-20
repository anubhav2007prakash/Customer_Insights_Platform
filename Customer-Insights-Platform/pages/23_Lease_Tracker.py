"""Tenant Lease Tracker — OmniMall AI. (#2 Kanban Lease Tracker)"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

import streamlit as st

from components.ui.cards import alert_banner, hero_section, metric_grid, section_header
from utils.page_bootstrap import bootstrap_page, finish_page

# ── Sample lease data ──────────────────────────────────────────────────────────
LEASES = [
    {"id": "L001", "tenant": "Zara",         "zone": "South Wing A", "sqft": 4200, "rent": 85000, "expires": 45,  "stage": "Active",       "contact": "Maria Santos",    "risk": "low"},
    {"id": "L002", "tenant": "Apple Store",  "zone": "Atrium East",  "sqft": 8500, "rent": 240000,"expires": 180, "stage": "Active",       "contact": "Jim Parsons",     "risk": "low"},
    {"id": "L003", "tenant": "H&M",          "zone": "North Wing B", "sqft": 6100, "rent": 92000, "expires": 22,  "stage": "Renewal",      "contact": "Anna Müller",     "risk": "high"},
    {"id": "L004", "tenant": "Starbucks",    "zone": "Food Court 1", "sqft": 1200, "rent": 32000, "expires": 88,  "stage": "Active",       "contact": "David Kim",       "risk": "low"},
    {"id": "L005", "tenant": "Nike",         "zone": "South Wing C", "sqft": 5400, "rent": 110000,"expires": 14,  "stage": "Negotiation",  "contact": "Sarah Chen",      "risk": "high"},
    {"id": "L006", "tenant": "Sephora",      "zone": "East Corridor","sqft": 2800, "rent": 68000, "expires": 60,  "stage": "Renewal",      "contact": "Luis García",     "risk": "medium"},
    {"id": "L007", "tenant": "AMC Theatres", "zone": "Level 3",      "sqft": 22000,"rent": 185000,"expires": 420, "stage": "Active",       "contact": "Rachel Wong",     "risk": "low"},
    {"id": "L008", "tenant": "Din Tai Fung", "zone": "Food Court 2", "sqft": 3200, "rent": 78000, "expires": 7,   "stage": "Negotiation",  "contact": "Peter Huang",     "risk": "high"},
    {"id": "L009", "tenant": "Gap",          "zone": "North Wing A", "sqft": 4800, "rent": 72000, "expires": 0,   "stage": "Prospect",     "contact": "Karen Bell",      "risk": "medium"},
    {"id": "L010", "tenant": "Lululemon",    "zone": "South Wing B", "sqft": 3600, "rent": 95000, "expires": 310, "stage": "Active",       "contact": "Alex Morgan",     "risk": "low"},
    {"id": "L011", "tenant": "Pandora",      "zone": "East Corridor","sqft": 900,  "rent": 28000, "expires": 35,  "stage": "Renewal",      "contact": "Emily Clarke",    "risk": "medium"},
    {"id": "L012", "tenant": "Uniqlo",       "zone": "North Wing C", "sqft": 7200, "rent": 108000,"expires": 0,   "stage": "Prospect",     "contact": "Hiro Tanaka",     "risk": "low"},
    {"id": "L013", "tenant": "Foot Locker",  "zone": "South Wing A", "sqft": 2600, "rent": 52000, "expires": 18,  "stage": "Negotiation",  "contact": "Marcus Davis",    "risk": "high"},
    {"id": "L014", "tenant": "Bath & Body",  "zone": "East Corridor","sqft": 1800, "rent": 44000, "expires": 195, "stage": "Active",       "contact": "Linda Torres",    "risk": "low"},
    {"id": "L015", "tenant": "Shake Shack",  "zone": "Food Court 1", "sqft": 1100, "rent": 38000, "expires": 0,   "stage": "Signed",       "contact": "James Okafor",   "risk": "low"},
]

STAGES = ["Prospect", "Negotiation", "Signed", "Renewal", "Active"]

STAGE_COLORS = {
    "Prospect":    ("#f3f4f6", "#6b7280"),
    "Negotiation": ("#fef9c3", "#b45309"),
    "Signed":      ("#dcfce7", "#15803d"),
    "Renewal":     ("#ede9fe", "#7c3aed"),
    "Active":      ("#e0f2fe", "#0369a1"),
}


def _due_class(days: int) -> str:
    if days <= 14:  return "urgent"
    if days <= 60:  return "soon"
    return "ok"


def _due_label(days: int) -> str:
    if days == 0:   return "New prospect"
    if days <= 14:  return f"⚠ Expires in {days}d"
    if days <= 60:  return f"Expires in {days}d"
    return f"Expires in {days}d"


def render_kanban() -> None:
    """Render the Kanban lease stage board."""
    section_header("Lease Pipeline Board", "Drag-and-drop view of every tenant lease stage")

    # Build columns HTML
    cols_html = ""
    for stage in STAGES:
        bg, color = STAGE_COLORS[stage]
        leases_in_stage = [l for l in LEASES if l["stage"] == stage]
        cards_html = ""
        for l in leases_in_stage:
            due_cls = _due_class(l["expires"])
            due_lbl = _due_label(l["expires"])
            risk_emoji = "🔴" if l["risk"] == "high" else "🟡" if l["risk"] == "medium" else "🟢"
            cards_html += f"""
            <div class="if-kanban-card" title="Contact: {l['contact']}">
              <div class="if-kanban-card-title">{risk_emoji} {l['tenant']}</div>
              <div class="if-kanban-card-sub">{l['zone']} · {l['sqft']:,} sqft</div>
              <div class="if-kanban-card-sub" style="margin-top:3px;">₹{l['rent']:,}/mo</div>
              <div class="if-kanban-card-footer">
                <span class="if-kanban-due {due_cls}">{due_lbl}</span>
                <span style="font-size:10px;color:#9ca3af;">{l['id']}</span>
              </div>
            </div>"""

        count = len(leases_in_stage)
        rent_total = sum(l["rent"] for l in leases_in_stage)
        cols_html += f"""
        <div class="if-kanban-col">
          <div class="if-kanban-col-header" style="color:{color};">
            <span>{stage.upper()}</span>
            <span style="background:{bg};color:{color};border-radius:20px;padding:2px 8px;font-size:10px;">{count}</span>
          </div>
          {cards_html if cards_html else '<div style="text-align:center;padding:20px;font-size:12px;color:#9ca3af;">Drop here</div>'}
          <div style="font-size:10px;color:#9ca3af;margin-top:8px;text-align:center;">
            Total ₹{rent_total:,}/mo
          </div>
        </div>"""

    st.html(f'<div class="if-kanban-board">{cols_html}</div>')
    st.caption("💡 Click any card for details · Colour: 🔴 High risk  🟡 Medium  🟢 Low")


def render_table_tab() -> None:
    """Render the full sortable lease table."""
    import pandas as pd
    section_header("All Leases", "Full lease portfolio with filters")

    col_filter, col_sort = st.columns([2, 1])
    with col_filter:
        stage_filter = st.multiselect("Filter by stage", STAGES, default=STAGES)
    with col_sort:
        risk_filter = st.multiselect("Risk", ["high", "medium", "low"], default=["high", "medium", "low"])

    df = pd.DataFrame(LEASES)
    df = df[df["stage"].isin(stage_filter) & df["risk"].isin(risk_filter)]
    df["expires_label"] = df["expires"].apply(lambda d: f"{d} days" if d > 0 else "New")
    df["monthly_rent"] = df["rent"].apply(lambda r: f"₹{r:,}")
    df["sqft_label"] = df["sqft"].apply(lambda s: f"{s:,} sqft")

    display = df[["id", "tenant", "zone", "sqft_label", "monthly_rent", "stage", "expires_label", "risk", "contact"]].copy()
    display.columns = ["ID", "Tenant", "Zone", "Area", "Monthly Rent", "Stage", "Expires In", "Risk", "Contact"]
    st.dataframe(display, use_container_width=True, hide_index=True)

    # Expiry alerts
    urgent = [l for l in LEASES if 0 < l["expires"] <= 30 and l["stage"] not in ["Signed"]]
    if urgent:
        section_header("⚠️ Expiry Alerts", "Leases expiring within 30 days")
        for l in urgent:
            st.html(f"""
            <div class="if-anomaly-card {'critical' if l['expires'] <= 14 else 'warning'}">
              <div class="if-anomaly-header">
                <span class="if-anomaly-title">🏬 {l['tenant']} — {l['zone']}</span>
                <span class="if-anomaly-sev {'critical' if l['expires'] <= 14 else 'warning'}">
                  Expires {l['expires']}d
                </span>
              </div>
              <div class="if-anomaly-body">
                Contact: {l['contact']} · ₹{l['rent']:,}/mo · {l['sqft']:,} sqft · Stage: {l['stage']}
              </div>
            </div>""")


def render_add_lease_tab() -> None:
    """Render the new lease form."""
    section_header("Add New Lease / Prospect", "Register a new tenant or renewal")
    with st.form("new_lease_form"):
        c1, c2 = st.columns(2)
        with c1:
            tenant_name = st.text_input("Tenant name", placeholder="e.g. Adidas")
            zone = st.selectbox("Zone", ["Atrium East", "North Wing A", "North Wing B", "North Wing C",
                                         "South Wing A", "South Wing B", "South Wing C",
                                         "East Corridor", "Food Court 1", "Food Court 2", "Level 3"])
            sqft = st.number_input("Area (sqft)", min_value=100, max_value=50000, value=2000, step=100)
        with c2:
            stage = st.selectbox("Initial stage", STAGES)
            rent = st.number_input("Monthly rent (₹)", min_value=5000, max_value=500000, value=50000, step=5000)
            contact = st.text_input("Contact person", placeholder="e.g. John Smith")
        note = st.text_area("Notes", placeholder="Any special terms, conditions, or context…", height=80)
        submitted = st.form_submit_button("Add to Pipeline", type="primary", use_container_width=True)
        if submitted:
            if tenant_name:
                st.success(f"✅ **{tenant_name}** added to pipeline as **{stage}** — ₹{rent:,}/mo · {sqft:,} sqft · {zone}")
                st.balloons()
            else:
                st.error("Tenant name is required.")


def main() -> None:
    bootstrap_page(
        "Lease Tracker",
        "lease_tracker",
        breadcrumbs=["Tenant Mgmt", "Lease Tracker"],
        subtitle="Kanban pipeline view of all tenant leases and renewals",
        icon="🏢",
    )

    metric_grid([
        {"label": "Active Leases",   "value": "15",     "change": 3.2,  "icon": "file-check",  "tone": "primary"},
        {"label": "Expiring <30d",   "value": "4",      "change": -1.0, "icon": "clock",       "tone": "warning"},
        {"label": "Monthly Revenue", "value": "₹13.3L", "change": 5.8,  "icon": "trending-up", "tone": "success"},
        {"label": "Prospects",       "value": "2",      "change": 100,  "icon": "user-plus",   "tone": "accent"},
    ], columns=4)

    alert_banner("warning", "Renewal queue", "3 leases need renewal action within 30 days. H&M, Nike, and Pandora.")

    tab1, tab2, tab3 = st.tabs(["📋 Kanban Board", "📊 All Leases", "➕ Add Lease"])
    with tab1: render_kanban()
    with tab2: render_table_tab()
    with tab3: render_add_lease_tab()

    finish_page()


main()
