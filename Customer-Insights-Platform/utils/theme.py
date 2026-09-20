"""Theme engine for InsightForge AI — light, dark, and auto modes."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Literal

import streamlit as st

from utils.constants import COLORS_DARK, COLORS_LIGHT, FONT_FAMILY

ThemeMode = Literal["light", "dark", "auto"]

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "styles"


def _css_variables(colors: dict[str, str]) -> str:
    """Generate CSS custom properties from a color palette."""
    lines = [f"  --if-{key.replace('_', '-')}: {value};" for key, value in colors.items()]
    return ":root {\n" + "\n".join(lines) + "\n}"


def _resolve_theme(mode: ThemeMode) -> str:
    if mode == "auto":
        return "dark"  # Streamlit cannot detect OS; default auto to dark
    return mode


class ThemeEngine:
    """Manages theme state and injects design-system CSS."""

    SESSION_KEY = "if_theme"

    @classmethod
    def init(cls) -> None:
        if cls.SESSION_KEY not in st.session_state:
            st.session_state[cls.SESSION_KEY] = "light"

    @classmethod
    def get_mode(cls) -> ThemeMode:
        cls.init()
        return st.session_state[cls.SESSION_KEY]

    @classmethod
    def set_mode(cls, mode: ThemeMode) -> None:
        st.session_state[cls.SESSION_KEY] = mode

    @classmethod
    def is_dark(cls) -> bool:
        return _resolve_theme(cls.get_mode()) == "dark"

    @classmethod
    def active_colors(cls) -> dict[str, str]:
        return COLORS_DARK if cls.is_dark() else COLORS_LIGHT

    @classmethod
    def _load_file(cls, filename: str) -> str:
        path = ASSETS_DIR / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    @classmethod
    def inject(cls) -> None:
        """Inject fonts, CSS variables, and stylesheets."""
        colors = cls.active_colors()
        main_css = cls._load_file("main.css")
        components_css = cls._load_file("components.css")
        dark_css = cls._load_file("dark_mode.css").replace(".if-theme-dark ", "") if cls.is_dark() else ""

        st.html(
            dedent(
                f"""
                <style>
                @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
                {_css_variables(colors)}
                html, body, [class*="css"] {{
                    font-family: {FONT_FAMILY} !important;
                }}
                {main_css}
                {components_css}
                {dark_css}
                </style>
                """
            )
        )

    @classmethod
    def chart_layout(cls) -> dict:
        """Plotly layout defaults aligned with active theme."""
        c = cls.active_colors()
        return {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"family": FONT_FAMILY, "color": c["text_secondary"], "size": 12},
            "margin": {"l": 24, "r": 24, "t": 40, "b": 24},
            "hoverlabel": {
                "bgcolor": c["card"],
                "font": {"family": FONT_FAMILY, "size": 13, "color": c["text_primary"]},
                "bordercolor": c["border_strong"],
            },
            "colorway": [
                c["chart_1"], c["chart_2"], c["chart_3"],
                c["chart_4"], c["chart_5"], c["chart_6"],
            ],
            "xaxis": {
                "gridcolor": "rgba(148, 163, 184, 0.12)",
                "linecolor": c["border"],
                "zerolinecolor": "rgba(148, 163, 184, 0.12)",
                "showgrid": True,
            },
            "yaxis": {
                "gridcolor": "rgba(148, 163, 184, 0.12)",
                "linecolor": c["border"],
                "zerolinecolor": "rgba(148, 163, 184, 0.12)",
                "showgrid": True,
            },
        }
