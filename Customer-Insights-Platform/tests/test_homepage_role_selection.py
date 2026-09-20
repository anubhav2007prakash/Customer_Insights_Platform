from utils.helpers import get_dashboard_context, get_homepage_role_options, set_homepage_role_selection


def test_homepage_role_options_are_grouped() -> None:
    grouped_roles = get_homepage_role_options()

    assert "Data & Analytics" in grouped_roles
    assert "Business & Operations" in grouped_roles
    assert "Administration & Governance" in grouped_roles
    assert "Data Analyst" in grouped_roles["Data & Analytics"]
    assert "Manager" in grouped_roles["Business & Operations"]
    assert "Admin" in grouped_roles["Administration & Governance"]


def test_homepage_role_selection_updates_session_state() -> None:
    import streamlit as st

    st.session_state.pop("if_user_role", None)
    st.session_state.pop("if_user_role_group", None)

    set_homepage_role_selection("Data Scientist")

    assert st.session_state["if_user_role"] == "Data Scientist"
    assert st.session_state["if_user_role_group"] == "Data & Analytics"


def test_dashboard_context_changes_by_role() -> None:
    analyst_context = get_dashboard_context("Data Analyst")
    manager_context = get_dashboard_context("Manager")
    admin_context = get_dashboard_context("Admin")

    assert analyst_context["focus"] == "Analysis"
    assert manager_context["focus"] == "Operations"
    assert admin_context["focus"] == "Governance"
    assert "data quality" in analyst_context["hero_copy"].lower()
    assert "team" in manager_context["hero_copy"].lower()
