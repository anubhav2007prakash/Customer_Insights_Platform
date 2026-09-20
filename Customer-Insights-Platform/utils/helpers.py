"""Shared helpers for InsightForge AI frontend."""

from __future__ import annotations

from datetime import datetime
from textwrap import dedent
from typing import Any

import streamlit as st

from utils.constants import APP_NAME, APP_TAGLINE
from utils.theme import ThemeEngine

HOME_PAGE_ROLE_GROUPS: dict[str, tuple[str, ...]] = {
    "Data & Analytics": (
        "Data Analyst",
        "Data Scientist",
        "BI Engineer",
        "Data Engineer",
    ),
    "Business & Operations": (
        "Manager",
        "Operations Lead",
        "Marketing Manager",
        "Sales Manager",
    ),
    "Administration & Governance": (
        "Admin",
        "Platform Admin",
        "Compliance Lead",
        "Executive",
    ),
}


def init_session_defaults() -> None:
    """Initialize common session state keys."""
    defaults = {
        "if_authenticated": True,
        "if_user_name": "Alex Morgan",
        "if_user_email": "alex.morgan@acmecorp.com",
        "if_user_role": "Admin",
        "if_org_name": "Acme Corporation",
        "if_workspace": "Production",
        "if_sidebar_collapsed": False,
        "if_notifications": 3,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_homepage_role_options() -> dict[str, tuple[str, ...]]:
    """Return the grouped role options displayed on the homepage."""
    return dict(HOME_PAGE_ROLE_GROUPS)


def set_homepage_role_selection(role: str) -> None:
    """Persist the selected homepage role and its group in session state."""
    group_name = next(
        (group for group, options in HOME_PAGE_ROLE_GROUPS.items() if role in options),
        "General",
    )
    st.session_state["if_user_role"] = role
    st.session_state["if_user_role_group"] = group_name


def get_dashboard_context(role: str) -> dict[str, str]:
    """Return dashboard copy tailored for the selected user role."""
    role_contexts: dict[str, dict[str, str]] = {
        "Data Analyst": {
            "focus": "Analysis",
            "hero_title": "Analyst workspace",
            "hero_copy": "Focus on data quality, trend discovery, and actionable insights for stakeholders.",
            "kpi_title": "Signal coverage",
            "recommendation_title": "Analyst recommendations",
        },
        "Data Scientist": {
            "focus": "Modeling",
            "hero_title": "Modeling workspace",
            "hero_copy": "Monitor experiments, refine features, and prioritize high-value predictive use cases.",
            "kpi_title": "Model readiness",
            "recommendation_title": "Modeling recommendations",
        },
        "Manager": {
            "focus": "Operations",
            "hero_title": "Operations workspace",
            "hero_copy": "Track delivery, team momentum, and the next decisions that matter most.",
            "kpi_title": "Operations pulse",
            "recommendation_title": "Team recommendations",
        },
        "Admin": {
            "focus": "Governance",
            "hero_title": "Governance workspace",
            "hero_copy": "Keep the platform healthy, govern access, and protect key business workflows.",
            "kpi_title": "Governance KPIs",
            "recommendation_title": "Governance actions",
        },
    }
    return role_contexts.get(role, role_contexts["Admin"])


def configure_page(
    page_title: str,
    *,
    layout: str = "wide",
    icon: str = ":material/analytics:",
) -> None:
    """Apply Streamlit page configuration."""
    st.set_page_config(
        page_title=f"{page_title} - {APP_NAME}",
        page_icon=icon,
        layout=layout,
        initial_sidebar_state="expanded",
    )
    ThemeEngine.init()
    init_session_defaults()
    ThemeEngine.inject()


def format_currency(value: float, compact: bool = False) -> str:
    """Format number as USD."""
    if compact:
        if abs(value) >= 1_000_000:
            return f"${value / 1_000_000:.1f}M"
        if abs(value) >= 1_000:
            return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def format_number(value: float, compact: bool = False) -> str:
    """Format large numbers."""
    if compact:
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        if abs(value) >= 1_000:
            return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def format_percent(value: float, signed: bool = True) -> str:
    """Format percentage with optional sign."""
    prefix = "+" if signed and value > 0 else ""
    return f"{prefix}{value:.1f}%"


def trend_class(value: float) -> str:
    """Return CSS class for positive/negative trend."""
    if value > 0:
        return "if-trend-up"
    if value < 0:
        return "if-trend-down"
    return "if-trend-neutral"


def relative_time(dt: datetime) -> str:
    """Human-readable relative time."""
    delta = datetime.now() - dt
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "Just now"
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def hide_streamlit_chrome() -> None:
    """Hide default Streamlit UI chrome for custom shell."""
    st.html(
        dedent(
            """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}

            /* Fully collapse the native header so it takes zero space */
            header[data-testid="stHeader"] {
                display: none !important;
                height: 0 !important;
                min-height: 0 !important;
                padding: 0 !important;
                overflow: hidden !important;
            }

            /* Remove the top padding that Streamlit adds to compensate for the header */
            .stApp > header + div {
                padding-top: 0 !important;
            }
            div[data-testid="stAppViewContainer"] > section:first-child {
                padding-top: 0 !important;
            }
            div[data-testid="stMainBlockContainer"] {
                padding-top: 0 !important;
            }

            .stApp {background: var(--if-background);}
            section[data-testid="stSidebar"] {display: none;}
            .block-container {
                padding-top: 0 !important;
                padding-bottom: 2rem !important;
                max-width: 100% !important;
            }
            .element-container {animation: fadeSlide 0.35s ease both;}
            @keyframes fadeSlide {
                from { opacity: 0; transform: translateY(8px); }
                to { opacity: 1; transform: translateY(0); }
            }
            </style>
            """
        )
    )


def plotly_config() -> dict[str, Any]:
    """Default Plotly chart config."""
    return {
        "displayModeBar": False,
        "responsive": True,
    }


def app_meta_html() -> str:
    """Return branded meta strip for auth pages."""
    return dedent(
        f"""
        <div class="if-auth-brand">
            <div class="if-auth-logo">IF</div>
            <div>
                <div class="if-auth-name">{APP_NAME}</div>
                <div class="if-auth-tagline">{APP_TAGLINE}</div>
            </div>
        </div>
        """
    ).strip()
