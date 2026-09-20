"""Register page — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from utils.helpers import configure_page, hide_streamlit_chrome, app_meta_html


def render_register_form() -> None:
    """Render the registration form."""
    with st.form("register_form"):
        c1, c2 = st.columns(2)
        with c1:
            first = st.text_input("First name")
        with c2:
            last = st.text_input("Last name")
        email = st.text_input("Work email")
        company = st.text_input("Company name")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

        if submitted:
            if not first or not last:
                st.error("Please enter both first and last name.")
            elif not email or "@" not in email:
                st.error("Please enter a valid work email.")
            elif not company:
                st.error("Please enter your company name.")
            elif not password or len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif not terms:
                st.error("Please accept the terms to continue.")
            else:
                st.session_state["if_authenticated"] = True
                st.session_state["if_user_name"] = f"{first} {last}"
                st.session_state["if_org_name"] = company
                st.session_state["if_user_email"] = email
                st.success("Account created successfully!")
                st.switch_page("pages/03_Onboarding.py")


def main() -> None:
    """Bootstrap and render the Register page."""
    configure_page("Create Account", icon="✨")
    hide_streamlit_chrome()

    st.markdown(app_meta_html(), unsafe_allow_html=True)
    st.markdown("### Create your account")
    st.markdown('<p class="if-caption">Start your 14-day enterprise trial</p>', unsafe_allow_html=True)

    render_register_form()

    st.page_link("pages/01_Login.py", label="Already have an account? Sign in")


main()
