"""Mall Loyalty Program — OmniMall AI."""

from __future__ import annotations

import streamlit as st
import pandas as pd
import random

from components.ui.cards import badge, empty_state, section_header, timeline
from utils.helpers import get_dashboard_context, relative_time
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_customers, get_customer_timeline, get_purchase_history


def init_loyalty_data():
    """Initialize the mall loyalty member database."""
    if "loyalty_db" not in st.session_state:
        st.session_state["loyalty_db"] = pd.DataFrame({
            "id": ["MAL-10001", "MAL-10002", "MAL-10003", "MAL-10004", "MAL-10005"],
            "name": ["Jane Doe", "John Smith", "Priya Patel", "Marcus Lee", "Emma Watson"],
            "email": ["jane.doe@example.com", "jsmith88@example.com", "priya.p@example.com", "marcus.l@example.com", "emma.w@example.com"],
            "tier": ["Gold", "Silver", "Platinum", "Bronze", "Gold"],
            "points": [12450, 4300, 89000, 150, 21800],
            "visits_ytd": [48, 12, 124, 2, 62],
            "lifetime_spend": [4200.00, 820.00, 34000.00, 45.00, 8100.00],
            "last_visit": ["2 days ago", "1 week ago", "Today", "1 month ago", "3 days ago"],
        })


def render_filters(df):
    """Render loyalty member search and filter controls."""
    fc1, fc2, fc3, fc4 = st.columns([2, 1, 1, 1])
    with fc1:
        search = st.text_input("Search", placeholder="Search by name, email or ID...", label_visibility="collapsed")
    with fc2:
        tier = st.selectbox("Loyalty Tier", ["All", "Platinum", "Gold", "Silver", "Bronze"], label_visibility="collapsed")
    with fc3:
        sort = st.selectbox("Sort", ["Highest Points", "Lifetime Spend", "Most Visits", "Recently Active"], label_visibility="collapsed")
    with fc4:
        bulk_action = st.selectbox("Action", ["Export to CSV", "Send Promo Email", "Issue Bonus Points"], label_visibility="collapsed")

    if search:
        df = df[df["name"].str.contains(search, case=False) | df["email"].str.contains(search, case=False)]
    if tier != "All":
        df = df[df["tier"] == tier]

    if sort == "Highest Points":
        df = df.sort_values("points", ascending=False)
    elif sort == "Lifetime Spend":
        df = df.sort_values("lifetime_spend", ascending=False)
    elif sort == "Most Visits":
        df = df.sort_values("visits_ytd", ascending=False)

    return df


def render_table_view(df) -> None:
    """Render the table view tab."""
    section_header(f"Mall Loyalty Member Directory · {len(df):,} members")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.TextColumn("Member ID"),
            "lifetime_spend": st.column_config.NumberColumn("Lifetime Spend", format="$%.2f"),
            "points": st.column_config.NumberColumn("Points Balance", format="%d pts"),
            "visits_ytd": st.column_config.NumberColumn("Visits YTD"),
        }
    )


def render_member_detail(df) -> None:
    """Render the detailed mall loyalty profile."""
    if len(df) == 0:
        st.info("No members match the current filters.")
        return

    selected = st.selectbox("Select Member Profile", df["name"].tolist())
    cust = df[df["name"] == selected].iloc[0]

    d1, d2 = st.columns([1, 2])
    with d1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        st.markdown(f"### {cust['name']}")
        st.markdown(f"**ID:** `{cust['id']}`")
        st.markdown(f"{cust['email']}")

        tone_map = {"Platinum": "primary", "Gold": "warning", "Silver": "neutral", "Bronze": "accent"}
        tone = tone_map.get(cust["tier"], "neutral")
        st.markdown(f"**Tier:** {badge(cust['tier'], tone)}", unsafe_allow_html=True)
        st.markdown(f"**Points Balance:** `{cust['points']:,}` pts")
        st.markdown(f"**Lifetime Spend:** `${cust['lifetime_spend']:,.2f}`")
        st.markdown(f"**Visits YTD:** `{cust['visits_ytd']}`")
        st.markdown(f"**Last Visit:** {cust['last_visit']}")

        st.divider()
        st.markdown("**Issue Bonus Points**")
        bonus_pts = st.number_input("Points to Award", min_value=0, value=100, key="bonus_pts_input")
        if st.button("Award Points", type="primary", use_container_width=True):
            idx = st.session_state["loyalty_db"].index[st.session_state["loyalty_db"]["name"] == selected].tolist()
            if idx:
                st.session_state["loyalty_db"].at[idx[0], "points"] += bonus_pts
                st.success(f"✅ {bonus_pts:,} points awarded to **{selected}**!")

        st.divider()
        st.markdown("**Member Notes**")
        note = st.text_area("Add note", placeholder="e.g. Prefers Luxury Wing, regular cinema-goer...", label_visibility="collapsed", key="cust_note")
        if st.button("Save Note", type="secondary", use_container_width=True):
            st.success("Note saved to loyalty profile.")
        st.markdown('</div>', unsafe_allow_html=True)

    with d2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        st.markdown("**Purchase History Across Mall Tenants**")
        random.seed(cust["name"])
        tenants = ["Zara", "Apple Store", "Starbucks", "AMC Theatres", "Sephora", "H&M", "Nike Flagship", "Din Tai Fung"]
        n_history = random.randint(2, 4)
        history = pd.DataFrame({
            "Date": ["2024-03-12", "2024-01-28", "2023-11-05", "2023-09-15"][:n_history],
            "Tenant": [random.choice(tenants) for _ in range(4)][:n_history],
            "Amount": [f"${random.randint(12, 1299)}.00" for _ in range(4)][:n_history],
            "Points Earned": [random.randint(12, 1299) for _ in range(4)][:n_history],
        })
        st.dataframe(history, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("**Loyalty Activity Timeline**")
        timeline(get_customer_timeline())
        st.markdown('</div>', unsafe_allow_html=True)


def render_points_redemption_tab() -> None:
    """Render the points redemption / reward store."""
    section_header("Points Redemption Center", "Manage loyalty reward redemptions and tier upgrades")

    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    st.dataframe(
        {
            "Reward": ["$10 Mall Gift Card", "$25 Mall Gift Card", "Free Parking (1 Day)", "VIP Cinema Ticket", "Complimentary Stroller Rental"],
            "Points Required": [1000, 2500, 500, 4000, 250],
            "Status": ["✅ Available", "✅ Available", "✅ Available", "✅ Available", "✅ Available"],
            "Redeemed Today": [42, 18, 88, 12, 34],
        },
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    with st.form("redeem_form"):
        st.markdown("**Process a Redemption**")
        c1, c2 = st.columns(2)
        with c1:
            member_id = st.text_input("Member ID", placeholder="e.g. MAL-10001")
            reward = st.selectbox("Reward", ["$10 Mall Gift Card", "$25 Mall Gift Card", "Free Parking (1 Day)", "VIP Cinema Ticket", "Complimentary Stroller Rental"])
        with c2:
            st.markdown("&nbsp;", unsafe_allow_html=True)
            st.markdown("**Points Cost**")
            st.markdown({"$10 Mall Gift Card": "1,000 pts", "$25 Mall Gift Card": "2,500 pts", "Free Parking (1 Day)": "500 pts", "VIP Cinema Ticket": "4,000 pts", "Complimentary Stroller Rental": "250 pts"}.get(reward, "—"))

        if st.form_submit_button("Process Redemption", type="primary"):
            if member_id:
                st.success(f"✅ **{reward}** redeemed for member `{member_id}`. Points deducted.")
            else:
                st.error("Please enter a valid Member ID.")


def render_churn_scorecard_tab() -> None:
    """Render #5 Churn Risk Scorecard tab."""
    section_header("⚠️ Churn Risk Scorecard", "AI-identified members & tenants at risk of non-renewal / inactivity")

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        st.html(
            """
            <div class="if-card if-churn-gauge-wrap">
                <div style="font-size:11px; font-weight:700; color:#6b7280; text-transform:uppercase;">Overall Portfolio Risk</div>
                <div class="if-churn-score medium">18.4%</div>
                <div style="font-size:12px; color:#f59e0b; font-weight:600; margin-top:4px;">🟡 Moderate Risk</div>
                <div style="font-size:11px; color:#6b7280; margin-top:8px;">Based on 30-day visit decay & lease expiry proximity</div>
            </div>
            """
        )
    with c2:
        st.markdown("**At-Risk Members & Accounts**")
        at_risk = [
            {"name": "Marcus Lee (MAL-10004)", "score": 88, "tier": "Bronze", "reason": "No visit in 32 days · Zero point redemptions", "level": "high"},
            {"name": "H&M (Tenant L003)", "score": 76, "tier": "Tenant", "reason": "Lease expires in 22 days · Footfall down 14%", "level": "high"},
            {"name": "John Smith (MAL-10002)", "score": 58, "tier": "Silver", "reason": "Visit frequency dropped from 4x/mo to 1x/mo", "level": "medium"},
            {"name": "Sephora (Tenant L006)", "score": 42, "tier": "Tenant", "reason": "Margin compression · Pending renewal discussion", "level": "medium"},
        ]
        for item in at_risk:
            bar_color = "#ef4444" if item['level'] == 'high' else "#f59e0b"
            st.html(
                f"""
                <div class="if-risk-row">
                    <div style="flex:1;">
                        <div style="font-size:13px; font-weight:600; color:#0f1028;">{item['name']}</div>
                        <div style="font-size:11px; color:#6b7280;">{item['reason']}</div>
                    </div>
                    <div style="width:80px;">
                        <div class="if-risk-bar" style="background:{bar_color}; width:{item['score']}%;"></div>
                    </div>
                    <div class="if-risk-pct" style="color:{bar_color};">{item['score']}%</div>
                </div>
                """
            )
    with c3:
        st.markdown("**Intervention Actions**")
        if st.button("🎁 Issue 500 Bonus Points", use_container_width=True):
            st.success("Bonus point offer dispatched to at-risk members!")
        if st.button("📧 Send Win-Back Email", use_container_width=True):
            st.success("Win-back email campaign launched!")
        if st.button("📞 Schedule Lease Meeting", use_container_width=True):
            st.success("Meeting invite sent to tenant contact!")


def main() -> None:
    """Bootstrap and render the Mall Loyalty Program page."""
    init_loyalty_data()

    bootstrap_page(
        "Loyalty Program",
        "customer_profile",
        breadcrumbs=["Marketing & Loyalty", "Loyalty Program"],
        subtitle="Manage loyalty program members, point balances, redemptions, and churn risk",
        icon="👤",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    section_header("OmniMall Loyalty Database")

    from utils.sample_data import get_kpis
    from components.ui.cards import metric_grid
    metric_grid([
        {"label": "Total Members", "value": "182,400", "change": 8.4, "icon": "users", "tone": "primary"},
        {"label": "Platinum Tier", "value": "2,840", "change": 4.2, "icon": "star", "tone": "accent"},
        {"label": "Points Issued MTD", "value": "4.2M", "change": 12.1, "icon": "zap", "tone": "success"},
        {"label": "Redemption Rate", "value": "34%", "change": 2.8, "icon": "gift", "tone": "warning"},
    ], columns=4)

    df = st.session_state["loyalty_db"].copy()
    df = render_filters(df)

    tab1, tab2, tab3, tab4 = st.tabs(["Member Directory", "Member Profile", "Points Redemption", "⚠️ Churn Risk"])

    with tab1:
        render_table_view(df)
    with tab2:
        render_member_detail(df)
    with tab3:
        render_points_redemption_tab()
    with tab4:
        render_churn_scorecard_tab()

    if len(df) == 0:
        empty_state("No members found", "Try adjusting your filters or search query.", "users", "Clear filters")

    finish_page()


main()
