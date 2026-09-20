"""Navigation registry for InsightForge AI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NavItem:
    """Single sidebar navigation entry."""

    id: str
    label: str
    icon: str
    page: str
    section: str = "Main"


@dataclass(frozen=True)
class NavSection:
    """Grouped navigation section."""

    title: str
    items: tuple[NavItem, ...]


def get_role_nav_sections(role: str | None = None) -> tuple[NavSection, ...]:
    """Return navigation sections filtered by persona."""
    role = role or "Admin"
    
    role_prefix = {
        "Data Analyst": "Analysis",
        "Data Scientist": "Modeling",
        "Manager": "Operations",
        "Admin": "Governance",
    }.get(role, "Workspace")

    def relabel(label: str) -> str:
        return f"{label} · {role_prefix}" if role_prefix != "Workspace" else label

    all_sections = {
        "Mall Overview": NavSection("Mall Overview", (
            NavItem("dashboard", relabel("Dashboard"), "layout-dashboard", "pages/04_Dashboard.py"),
            NavItem("ai_center", relabel("AI Center"), "bot", "pages/09_AI_Center.py"),
            NavItem("data_import", relabel("Data Import"), "upload", "pages/05_Data_Ingestion.py"),
            NavItem("reports", relabel("Reports"), "file-text", "pages/20_Reports.py"),
        )),
        "Tenant Management": NavSection("Tenant Management", (
            NavItem("data_manager", relabel("Tenant Directory"), "database", "pages/18_Data_Manager.py"),
            NavItem("lease_tracker", relabel("Lease Tracker"), "file-check", "pages/23_Lease_Tracker.py"),
            NavItem("sales", relabel("Concierge Desk"), "monitor", "pages/17_Sales.py"),
        )),
        "Mall Operations": NavSection("Mall Operations", (
            NavItem("analytics", relabel("Mall Traffic"), "bar-chart-2", "pages/07_Analytics.py"),
            NavItem("admin", relabel("Facilities & Security"), "building", "pages/21_Admin.py"),
            NavItem("settings", relabel("Settings"), "settings", "pages/22_Settings.py"),
        )),
        "Marketing & Loyalty": NavSection("Marketing & Loyalty", (
            NavItem("customers", relabel("Mall Loyalty"), "users", "pages/06_Customer_Profile.py"),
            NavItem("marketing", relabel("Mall Campaigns"), "megaphone", "pages/16_Marketing.py"),
            NavItem("forecasting", relabel("Event Forecasting"), "trending-up", "pages/13_Forecasting.py"),
            NavItem("recommendations", relabel("Cross-Promotion AI"), "zap", "pages/15_Recommendations.py"),
        )),
    }

    if role in ["Data Analyst", "BI Engineer", "Data Engineer"]:
        allowed = ["Mall Overview", "Mall Operations"]
    elif role in ["Data Scientist"]:
        allowed = ["Mall Overview", "Marketing & Loyalty"]
    elif role in ["Manager", "Operations Lead", "Executive"]:
        allowed = ["Mall Overview", "Tenant Management", "Mall Operations", "Marketing & Loyalty"]
    elif role in ["Marketing Manager", "Sales Manager"]:
        allowed = ["Mall Overview", "Marketing & Loyalty"]
    elif role in ["Admin", "Platform Admin", "Compliance Lead"]:
        allowed = list(all_sections.keys())
    else:
        allowed = ["Mall Overview"]
        
    return tuple(all_sections[sec] for sec in allowed if sec in all_sections)


NAV_SECTIONS: tuple[NavSection, ...] = get_role_nav_sections("Admin")


def all_nav_items() -> list[NavItem]:
    """Flatten all navigation items."""
    items: list[NavItem] = []
    for section in NAV_SECTIONS:
        items.extend(section.items)
    return items


def find_nav_by_id(nav_id: str) -> NavItem | None:
    """Find navigation item by id."""
    for item in all_nav_items():
        if item.id == nav_id:
            return item
    return None
