"""InsightForge AI application entry point."""

from __future__ import annotations

from textwrap import dedent

import streamlit as st

from bootstrap import bootstrap
from utils.constants import APP_NAME, APP_TAGLINE
from utils.helpers import (
    configure_page,
    get_homepage_role_options,
    hide_streamlit_chrome,
    set_homepage_role_selection,
)
from utils.icons import icon


def render_hero() -> None:
    """Render the landing hero section."""
    st.html(
        dedent(
            f"""
            <div class="if-landing-shell if-fade-in">
                <div class="if-landing-hero">
                    <div class="if-landing-copy">
                        <div class="if-pill-row">
                            <span class="if-pill">{APP_NAME}</span>
                            <span class="if-pill">AI-powered planning</span>
                            <span class="if-pill">Role-based workspace</span>
                        </div>
                        <div class="if-display">Welcome to your modern operating layer.</div>
                        <p class="if-body" style="max-width:620px;margin:12px 0 0;line-height:1.7">{APP_TAGLINE}</p>
                        <div class="if-landing-actions">
                            <div class="if-btn if-btn-primary">Start onboarding</div>
                            <div class="if-btn if-btn-secondary">Explore the dashboard</div>
                        </div>
                        <div class="if-stat-strip">
                            <span class="if-badge primary">360° visibility</span>
                            <span class="if-badge success">Live recommendations</span>
                            <span class="if-badge neutral">Built for fast decisions</span>
                        </div>
                    </div>
                    <div class="if-landing-panel">
                        <div class="if-panel-label">Workspace snapshot</div>
                        <div class="if-panel-value">Faster insights, cleaner action.</div>
                        <div class="if-story-copy">Bring customer health, forecasts, and AI recommendations into one calm, high-signal workspace.</div>
                        <div class="if-landing-panel-grid">
                            <div class="if-landing-metric">
                                <div class="if-panel-label">Signals</div>
                                <div class="if-panel-value">24/7</div>
                            </div>
                            <div class="if-landing-metric">
                                <div class="if-panel-label">Focus</div>
                                <div class="if-panel-value">Role-fit</div>
                            </div>
                            <div class="if-landing-metric">
                                <div class="if-panel-label">Surfaces</div>
                                <div class="if-panel-value">12+</div>
                            </div>
                            <div class="if-landing-metric">
                                <div class="if-panel-label">Speed</div>
                                <div class="if-panel-value">Instant</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
        )
    )


def render_command_intro() -> None:
    """Render the command center intro card."""
    st.html(
        """
    <div class="if-home-command">
      <div class="if-home-command-card">
        <div class="if-label">Welcome to InsightForge AI</div>
        <div class="if-h3" style="margin-top:6px;">A calm, high-signal workspace for the people making decisions every day.</div>
        <div class="if-body" style="margin-top:8px;">Choose your role, add a few details, and step into a tailored operating layer built for faster follow-through.</div>
        <div class="if-home-command-pillrow">
          <span class="if-home-command-pill">● Personalized onboarding</span>
          <span class="if-home-command-pill">● Role-aware insights</span>
          <span class="if-home-command-pill">● Faster action loops</span>
        </div>
      </div>
      <div class="if-home-command-card">
        <div class="if-home-command-metric">
          <strong>Workspace readiness</strong>
          <span>Ready</span>
        </div>
        <div class="if-home-command-metric">
          <strong>Adaptive signals</strong>
          <span>12+ live surfaces</span>
        </div>
        <div class="if-home-command-metric">
          <strong>Time to value</strong>
          <span>Under 2 minutes</span>
        </div>
      </div>
    </div>
    """
    )


def render_form_styles() -> None:
    """Inject custom form and input styles."""
    st.html(
        """
    <style>
    div[data-testid="stForm"] > div {
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(229,231,235,0.95);
        border-radius: 22px;
        padding: 18px;
        box-shadow: 0 18px 42px rgba(15, 23, 42, 0.06);
    }
    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] input,
    div[data-testid="stTextArea"] textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(203,213,225,0.95) !important;
        box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.03);
        padding: 10px 12px;
    }
    .stButton > button {
        border-radius: 999px !important;
        padding: 0.55rem 1rem;
        font-weight: 600;
        box-shadow: 0 10px 24px rgba(79, 70, 229, 0.15);
    }
    </style>
    """
    )


def render_onboarding_steps() -> None:
    """Render the 3-step onboarding guide cards."""
    st.markdown(
        '<div class="if-step-grid">'
        '<div class="if-step-card"><div class="if-step-number">1</div><div class="if-card-title">Pick your role</div><div class="if-card-subtitle" style="margin-top:6px;">Select the persona that matches your daily work so the platform highlights the right signals.</div></div>'
        '<div class="if-step-card"><div class="if-step-number">2</div><div class="if-card-title">Complete profile</div><div class="if-card-subtitle" style="margin-top:6px;">Add a few details to make navigation, recommendations, and reporting feel native to your team.</div></div>'
        '<div class="if-step-card"><div class="if-step-number">3</div><div class="if-card-title">Open your workspace</div><div class="if-card-subtitle" style="margin-top:6px;">Step into a dashboard that feels calm, focused, and ready for real decisions.</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_profile_form(role_options: dict, role_labels: list[str], flattened_options: list[str]) -> None:
    """Render the profile setup form with role selection and user details."""
    selected_role = st.session_state.get("if_user_role", "Admin")

    with st.form("home_profile_form"):
        st.markdown("#### Choose your user role")
        st.caption("Select the role that best matches your day-to-day work and share a few details to personalize the experience.")

        default_index = 0
        if selected_role in flattened_options:
            try:
                label = f"{selected_role} ({next(group for group, options in role_options.items() if selected_role in options)})"
                default_index = role_labels.index(label)
            except (StopIteration, ValueError):
                default_index = 0

        selected_label = st.selectbox(
            "User role",
            options=role_labels,
            index=default_index,
            key="homepage_role_dropdown",
            help="Choose the role that best fits your work profile.",
        )

        st.markdown("#### Profile details")
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Full name", value=st.session_state.get("if_user_name", "Alex Morgan"))
            email = st.text_input("Email address", value=st.session_state.get("if_user_email", "alex.morgan@acmecorp.com"))
            phone = st.text_input("Phone number", value=st.session_state.get("if_user_phone", ""), help="Optional")
        with c2:
            company = st.text_input("Company", value=st.session_state.get("if_org_name", "Acme Corporation"))
            password = st.text_input("Password", type="password", value=st.session_state.get("if_user_password", ""), help="Use a strong password")
            department = st.text_input("Department", value=st.session_state.get("if_user_department", "Data & Analytics"))

        submitted = st.form_submit_button("Save profile", use_container_width=True, type="primary")
        if submitted:
            # Persist role selection only on submit
            if selected_label:
                chosen_role = selected_label.split(" (", 1)[0]
                set_homepage_role_selection(chosen_role)

            is_valid = True
            if "@" not in email or "." not in email:
                st.error("Please enter a valid email address.")
                is_valid = False
            if phone and len(phone.replace("+", "").replace("-", "").replace(" ", "")) < 7:
                st.error("Please enter a valid phone number.")
                is_valid = False
            if password and len(password) < 6:
                st.error("Password should be at least 6 characters long.")
                is_valid = False
            if is_valid:
                st.session_state["if_user_name"] = full_name or "Alex Morgan"
                st.session_state["if_user_email"] = email or "alex.morgan@acmecorp.com"
                st.session_state["if_user_phone"] = phone or ""
                st.session_state["if_org_name"] = company or "Acme Corporation"
                st.session_state["if_user_password"] = password or ""
                st.session_state["if_user_department"] = department or "Data & Analytics"
                st.session_state["if_authenticated"] = True
                st.session_state["home_profile_completed"] = True
                st.success("Profile details saved. Preparing your workspace...")
                st.markdown(
                    '<div class="if-card" style="padding:16px 18px;margin-top:10px">'
                    '<div class="if-card-title">Welcome aboard</div>'
                    '<div class="if-card-subtitle">Your personalized dashboard is loading now with your selected role and profile details.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.progress(0.5, text="Preparing your workspace...")
                with st.spinner("Opening your dashboard..."):
                    pass
                st.progress(1.0, text="Almost ready...")
                st.switch_page("pages/04_Dashboard.py")


def render_platform_highlights() -> None:
    """Render the 4-column platform highlights row."""
    st.markdown("#### Platform Highlights")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.html(
            f'<div class="if-landing-highlight"><div class="if-card-title">AI Insights</div>'
            f'<div class="if-card-subtitle" style="margin-top:6px">{icon("sparkles", 16, "var(--if-primary)")} Automated discovery with responsive signals.</div></div>'
        )
    with c2:
        st.html(
            f'<div class="if-landing-highlight"><div class="if-card-title">Analytics</div>'
            f'<div class="if-card-subtitle" style="margin-top:6px">{icon("bar-chart-3", 16, "var(--if-primary)")} Clear, high-contrast reporting surfaces.</div></div>'
        )
    with c3:
        st.html(
            f'<div class="if-landing-highlight"><div class="if-card-title">Customers</div>'
            f'<div class="if-card-subtitle" style="margin-top:6px">{icon("users", 16, "var(--if-primary)")} 360-degree intelligence for every team.</div></div>'
        )
    with c4:
        st.html(
            f'<div class="if-landing-highlight"><div class="if-card-title">Integrations</div>'
            f'<div class="if-card-subtitle" style="margin-top:6px">{icon("plug", 16, "var(--if-primary)")} CRM and commerce workflows that feel connected.</div></div>'
        )


def main() -> None:
    """Main entry point — bootstrap, render landing and profile form."""
    bootstrap()
    configure_page(APP_NAME)
    hide_streamlit_chrome()

    render_hero()
    render_command_intro()
    render_form_styles()
    render_onboarding_steps()

    role_options = get_homepage_role_options()
    flattened_options = [role for group_options in role_options.values() for role in group_options]
    role_labels = [f"{role} ({group_name})" for group_name, group_options in role_options.items() for role in group_options]

    render_profile_form(role_options, role_labels, flattened_options)

    if "if_user_role" in st.session_state:
        st.success(f"Current selection: {st.session_state['if_user_role']} • {st.session_state.get('if_user_role_group', 'General')}")

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.page_link("pages/01_Login.py", label="Sign In")
    with col2:
        st.page_link("pages/04_Dashboard.py", label="Open Dashboard")
    with col3:
        st.page_link("pages/02_Register.py", label="Create Account")

    st.markdown("---")
    render_platform_highlights()


main()
