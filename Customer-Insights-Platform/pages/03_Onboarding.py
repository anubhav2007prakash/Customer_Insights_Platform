"""Onboarding wizard — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.ui.cards import progress_bar
from utils.helpers import configure_page, hide_streamlit_chrome, app_meta_html


def render_organization_step() -> None:
    """Render organization configuration step."""
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Organization name", value=st.session_state.get("if_org_name", ""), key="onboarding_org_name")
        st.selectbox("Industry", ["Technology", "Retail", "Finance", "Healthcare", "Manufacturing"], key="onboarding_industry")
    with c2:
        st.selectbox("Company size", ["1-50", "51-200", "201-1000", "1000+"], key="onboarding_company_size")
        st.selectbox("Primary goal", ["Reduce churn", "Increase revenue", "Improve retention", "AI insights"], key="onboarding_goal")


def render_integrations_step() -> None:
    """Render integrations configuration step."""
    st.multiselect("Connect data sources", ["Salesforce", "HubSpot", "Shopify", "Stripe", "Google Analytics"], default=["Salesforce"], key="onboarding_integrations")
    st.file_uploader("Upload sample dataset (CSV)", type=["csv"], key="onboarding_file")


def render_team_step() -> None:
    """Render team invites step."""
    st.text_area("Invite teammates (one email per line)", placeholder="colleague@company.com", key="onboarding_invites")


def main() -> None:
    """Bootstrap and render Onboarding page."""
    configure_page("Onboarding", icon="🚀")
    hide_streamlit_chrome()

    st.markdown(app_meta_html(), unsafe_allow_html=True)
    st.markdown("### Set up your workspace")

    # Dynamic step progress
    step = st.radio("Onboarding step", ["Organization", "Integrations", "Invite team"], horizontal=True, label_visibility="collapsed")

    if step == "Organization":
        progress_bar(33, "Step 1 of 3 — Configure your organization")
        render_organization_step()
    elif step == "Integrations":
        progress_bar(66, "Step 2 of 3 — Connect integrations & data")
        render_integrations_step()
    else:
        progress_bar(100, "Step 3 of 3 — Invite your team")
        render_team_step()

    st.markdown("---")
    if st.button("Complete setup", type="primary", use_container_width=True):
        st.session_state["if_authenticated"] = True
        # Save onboarding state
        st.session_state["if_onboarding_completed"] = True
        # Save organization name if changed
        if st.session_state.get("onboarding_org_name"):
            st.session_state["if_org_name"] = st.session_state["onboarding_org_name"]

        st.balloons()
        st.success("Setup complete! Redirecting to Dashboard...")
        st.switch_page("pages/04_Dashboard.py")


main()
