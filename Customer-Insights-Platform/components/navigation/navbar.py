"""Top navigation bar for InsightForge AI."""

from __future__ import annotations

from typing import Sequence

import streamlit as st

from utils.icons import icon
from utils.theme import ThemeEngine


def render_breadcrumbs(crumbs: Sequence[str]) -> str:
    """Build breadcrumb HTML."""
    if not crumbs:
        return ""
    parts = []
    for i, c in enumerate(crumbs):
        sep = icon("chevron-right", 12, "var(--if-text-muted)") if i > 0 else ""
        parts.append(f"{sep}<span>{c}</span>")
    return f'<div class="if-breadcrumb">{"".join(parts)}</div>'


def render_topbar(title: str, breadcrumbs: Sequence[str] | None = None) -> None:
    """Render top bar with search, notifications, shortcuts, profile, and theme controls."""
    crumbs = list(breadcrumbs) if breadcrumbs else [title]
    notif_count = st.session_state.get("if_notifications", 0)
    user_name = st.session_state.get("if_user_name", "User")
    user_role = st.session_state.get("if_user_role", "Admin")
    role_group = st.session_state.get("if_user_role_group", "General")
    role_suffix = {
        "Data Analyst": "Analysis",
        "Data Scientist": "Modeling",
        "Manager": "Operations",
        "Admin": "Governance",
    }.get(user_role, "Workspace")
    initials = "".join(w[0] for w in user_name.split()[:2]).upper()
    notif_dot = '<span class="if-badge-dot"></span>' if notif_count else ""

    tb1, tb2, tb3, tb4, tb5, tb6, tb7 = st.columns([3.2, 1.3, 0.45, 0.45, 0.45, 0.5, 1.6])

    with tb1:
        st.markdown(
            f"""
            <div class="if-topbar" style="position:relative;height:auto;padding:12px 0;border:none;background:transparent">
                <div class="if-topbar-left">{render_breadcrumbs(crumbs)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tb2:
        search_query = st.text_input("Search", placeholder="Search pages…", label_visibility="collapsed", key=f"search_{title}")
        if search_query:
            q = search_query.lower()
            routes = {
                "dash": "pages/04_Dashboard.py",
                "customer": "pages/06_Customer_Profile.py",
                "analytic": "pages/07_Analytics.py",
                "advanced": "pages/08_Advanced_Analytics.py",
                "report": "pages/20_Reports.py",
                "admin": "pages/21_Admin.py",
                "setting": "pages/22_Settings.py",
            }
            matched = False
            for key, path in routes.items():
                if key in q:
                    st.session_state[f"search_{title}"] = "" # clear search
                    st.switch_page(path)
                    matched = True
                    break
            
            if not matched:
                st.toast(f"No page found matching '{search_query}'", icon="🔍")
                st.session_state[f"search_{title}"] = ""

    with tb3:
        with st.popover("🤖", help="Open AI Assistant"):
            st.markdown("**InsightForge AI**")
            chat_container = st.container(height=300)
            if "if_ai_chat_history" not in st.session_state:
                st.session_state["if_ai_chat_history"] = [{"role": "assistant", "content": f"Hi {user_name.split()[0]}! How can I help you analyze your {role_suffix.lower()} data today?"}]
            
            for msg in st.session_state["if_ai_chat_history"]:
                chat_container.chat_message(msg["role"]).write(msg["content"])
                
            if prompt := st.chat_input("Ask InsightForge AI..."):
                st.session_state["if_ai_chat_history"].append({"role": "user", "content": prompt})
                chat_container.chat_message("user").write(prompt)
                
                # Mock AI response
                response = f"I am analyzing your query regarding '{prompt}'. In a production environment, this would query your real-time data."
                st.session_state["if_ai_chat_history"].append({"role": "assistant", "content": response})
                chat_container.chat_message("assistant").write(response)
                st.rerun()

    with tb4:
        with st.popover("🔔", help="Notifications"):
            st.markdown("**Notifications**")
            # Generate mock notifications based on role
            role_notifs = {
                "Data Analyst": ["New data quality issue in Q3 dataset", "Report 'Weekly Sales' finished generating"],
                "Data Scientist": ["Model 'ChurnPredict_v3' deployed successfully", "Experiment 'Pricing_A_B' reached significance"],
                "Manager": ["Revenue target reached for NA Region", "Weekly team performance summary ready"],
                "Admin": ["New user role request pending", "System maintenance scheduled for tonight"]
            }
            notifs = role_notifs.get(user_role, ["Welcome to InsightForge AI", "System running normally"])
            for n in notifs:
                st.info(n, icon="💬")
            if st.button("Mark all as read", use_container_width=True):
                st.session_state["if_notifications"] = 0
                st.rerun()
    with tb5:
        if st.button("☀", key=f"theme_light_{title}", help="Light Theme"):
            ThemeEngine.set_mode("light")
            st.rerun()
    with tb6:
        if st.button("🌙", key=f"theme_dark_{title}", help="Dark Theme"):
            ThemeEngine.set_mode("dark")
            st.rerun()
    with tb7:
        st.markdown(
            f"""
            <div class="if-profile-chip" style="margin-top:4px;padding:8px 10px;border-radius:14px;background:rgba(255,255,255,0.92);border:1px solid rgba(229,231,235,0.95);box-shadow:0 8px 18px rgba(15,23,42,0.04)">
                <div class="if-avatar">{initials}</div>
                <div class="if-profile-meta">
                    <div class="if-profile-name">{user_name}</div>
                    <div class="if-profile-role">{user_role}</div>
                    <div class="if-profile-role" style="font-size:10px;opacity:0.75">{role_group} · {role_suffix}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
