"""Page bootstrap utilities."""

from __future__ import annotations

from components.layouts.app_shell import close_page, render_page
from utils.helpers import configure_page


def bootstrap_page(
    title: str,
    active_nav: str,
    *,
    breadcrumbs: list[str] | None = None,
    subtitle: str = "",
    icon: str = "📊",
) -> None:
    """Configure Streamlit and open the app shell."""
    configure_page(title, icon=icon)
    render_page(
        title=title,
        active_nav=active_nav,
        breadcrumbs=breadcrumbs,
        subtitle=subtitle,
    )


def finish_page() -> None:
    """Close the app shell."""
    close_page()
