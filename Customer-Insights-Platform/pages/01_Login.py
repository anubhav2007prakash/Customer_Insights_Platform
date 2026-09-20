"""Login page for InsightForge AI."""

from __future__ import annotations

from textwrap import dedent

import streamlit as st

from utils.constants import APP_NAME, APP_TAGLINE
from utils.helpers import app_meta_html, configure_page, hide_streamlit_chrome
from utils.icons import icon


def render_hero_panel() -> None:
    """Render the brand/hero left column."""
    st.html(
        dedent(
            f"""
            <div class="if-auth-hero" style="min-height:95vh;border-radius:0">
                <div style="font-size:14px;opacity:0.8;margin-bottom:24px">Enterprise Customer Intelligence</div>
                <div class="if-display" style="color:#fff;margin-bottom:16px">{APP_NAME}</div>
                <p style="font-size:16px;opacity:0.9;line-height:1.7;max-width:420px">{APP_TAGLINE}</p>
                <div style="margin-top:48px;display:grid;gap:16px">
                    <div style="display:flex;gap:12px;align-items:center">
                        {icon('sparkles', 20, '#fff')} <span>AI-powered business insights</span>
                    </div>
                    <div style="display:flex;gap:12px;align-items:center">
                        {icon('shield', 20, '#fff')} <span>Enterprise-grade security</span>
                    </div>
                    <div style="display:flex;gap:12px;align-items:center">
                        {icon('bar-chart-3', 20, '#fff')} <span>Advanced analytics &amp; forecasting</span>
                    </div>
                </div>
            </div>
            """
        )
    )


def render_login_form() -> None:
    """Render the sign-in form panel."""
    st.html(app_meta_html())
    st.markdown("### Welcome back")
    st.html('<p class="if-caption">Sign in to your workspace</p>')

    with st.form("login_form"):
        email = st.text_input("Work email", placeholder="you@company.com")
        password = st.text_input("Password", type="password", placeholder="********")
        _remember = st.checkbox("Remember me for 30 days")
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        if submitted:
            st.session_state["if_authenticated"] = True
            st.session_state["if_user_email"] = email or "alex.morgan@acmecorp.com"
            st.success("Authenticated successfully.")
            st.switch_page("pages/04_Dashboard.py")

    st.markdown("---")
    st.page_link("pages/02_Register.py", label="Create an account")
    st.page_link("pages/03_Onboarding.py", label="New user? Complete onboarding")


def main() -> None:
    """Bootstrap and render the login page."""
    configure_page("Sign In")
    hide_streamlit_chrome()

    st.html(
        dedent(
            """
            <style>
            .if-auth-wrap { display: grid; grid-template-columns: 1fr 1fr; min-height: 95vh; }
            @media (max-width: 900px) {
                .if-auth-wrap { grid-template-columns: 1fr; }
                .if-auth-hero { display: none; }
            }
            </style>
            """
        )
    )

    hero, panel = st.columns([1, 1])
    with hero:
        render_hero_panel()
    with panel:
        render_login_form()



main()
