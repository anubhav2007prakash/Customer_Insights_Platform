"""Application shell — sidebar, topbar, and page wrapper."""

from __future__ import annotations

from typing import Sequence

import streamlit as st

from components.navigation.navbar import render_topbar
from components.navigation.sidebar import render_sidebar
from utils.helpers import hide_streamlit_chrome


def get_sidebar_layout(collapsed: bool) -> tuple[float, float]:
    """Return the column split used by the shell when the sidebar is collapsed or expanded."""
    return (0.07, 0.93) if collapsed else (0.17, 0.83)


def render_page(
    title: str,
    *,
    active_nav: str,
    breadcrumbs: Sequence[str] | None = None,
    subtitle: str = "",
) -> None:
    """Render the full application shell for authenticated pages."""
    hide_streamlit_chrome()

    collapsed = st.session_state.get("if_sidebar_collapsed", False)
    nav_col, main_col = st.columns(get_sidebar_layout(collapsed), gap="small")

    with nav_col:
        render_sidebar(active_nav)

    with main_col:
        render_topbar(title, breadcrumbs=breadcrumbs)

        # ── Live status ticker ─────────────────────────────────────────────
        st.html("""
        <div class="if-ticker-wrap">
          <div class="if-ticker-track">
            <span class="if-ticker-item">📡 Live Footfall &nbsp;28,400 &nbsp;<span class="if-ticker-delta up">▲ +8.4%</span></span>
            <span class="if-ticker-sep">|</span>
            <span class="if-ticker-item">🏬 Active Tenants &nbsp;247 &nbsp;<span class="if-ticker-delta up">▲ +3</span></span>
            <span class="if-ticker-sep">|</span>
            <span class="if-ticker-item">💰 Today's Sales &nbsp;₹4.2 Cr &nbsp;<span class="if-ticker-delta up">▲ +11.4%</span></span>
            <span class="if-ticker-sep">|</span>
            <span class="if-ticker-item">🅿️ Parking &nbsp;82% Full</span>
            <span class="if-ticker-sep">|</span>
            <span class="if-ticker-item">🔔 Maintenance Alerts &nbsp;<span class="if-ticker-delta warn">4 open</span></span>
            <span class="if-ticker-sep">|</span>
            <span class="if-ticker-item">⚡ AI Models &nbsp;Online &nbsp;<span class="if-ticker-delta up">●</span></span>
            <span class="if-ticker-sep">|</span>
            <span class="if-ticker-item">📡 Live Footfall &nbsp;28,400 &nbsp;<span class="if-ticker-delta up">▲ +8.4%</span></span>
            <span class="if-ticker-sep">|</span>
            <span class="if-ticker-item">🏬 Active Tenants &nbsp;247 &nbsp;<span class="if-ticker-delta up">▲ +3</span></span>
            <span class="if-ticker-sep">|</span>
            <span class="if-ticker-item">💰 Today's Sales &nbsp;₹4.2 Cr &nbsp;<span class="if-ticker-delta up">▲ +11.4%</span></span>
            <span class="if-ticker-sep">|</span>
            <span class="if-ticker-item">🅿️ Parking &nbsp;82% Full</span>
            <span class="if-ticker-sep">|</span>
            <span class="if-ticker-item">🔔 Maintenance Alerts &nbsp;<span class="if-ticker-delta warn">4 open</span></span>
            <span class="if-ticker-sep">|</span>
            <span class="if-ticker-item">⚡ AI Models &nbsp;Online &nbsp;<span class="if-ticker-delta up">●</span></span>
          </div>
        </div>
        <style>
        .if-ticker-wrap {
          width: 100%;
          overflow: hidden;
          background: linear-gradient(90deg, rgba(99,102,241,0.07) 0%, rgba(37,99,235,0.04) 100%);
          border: 1px solid rgba(99,102,241,0.14);
          border-radius: 10px;
          padding: 0;
          margin: 4px 0 10px;
          height: 34px;
          display: flex;
          align-items: center;
        }
        .if-ticker-track {
          display: inline-flex;
          align-items: center;
          white-space: nowrap;
          animation: if-ticker-scroll 32s linear infinite;
          gap: 0;
        }
        .if-ticker-wrap:hover .if-ticker-track {
          animation-play-state: paused;
        }
        @keyframes if-ticker-scroll {
          from { transform: translateX(0); }
          to   { transform: translateX(-50%); }
        }
        .if-ticker-item {
          font-size: 12px;
          font-weight: 500;
          color: var(--if-text-secondary, #374151);
          padding: 0 18px;
          letter-spacing: 0.01em;
        }
        .if-ticker-sep {
          color: rgba(99,102,241,0.3);
          font-weight: 300;
          font-size: 14px;
          flex-shrink: 0;
        }
        .if-ticker-delta {
          font-weight: 700;
          font-size: 11px;
        }
        .if-ticker-delta.up   { color: #10b981; }
        .if-ticker-delta.warn { color: #f59e0b; }
        .if-ticker-delta.down { color: #ef4444; }
        </style>
        """)
        # ──────────────────────────────────────────────────────────────────

        st.markdown('<div class="if-page-content if-fade-in">', unsafe_allow_html=True)

        if subtitle:
            st.markdown(
                f"""
                <div class="if-page-header">
                    <div class="if-h2">{title}</div>
                    <div class="if-body" style="margin-top:4px">{subtitle}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif not breadcrumbs:
            st.markdown(
                f'<div class="if-page-header"><div class="if-h2">{title}</div></div>',
                unsafe_allow_html=True,
            )



def close_page() -> None:
    """Render a floating AI assistant affordance for premium shell experience."""
    st.html(
        """
        <div class="if-floating-ai" title="Open AI assistant">
            <a href="/AI%20Business%20Analyst" target="_self">✦</a>
        </div>
        """
    )
    return None
