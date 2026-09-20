"""Reusable UI components for InsightForge AI."""

from __future__ import annotations

from textwrap import dedent
from typing import Any

import streamlit as st

from utils.helpers import format_percent, relative_time, trend_class
from utils.icons import icon
from utils.theme import ThemeEngine


def _html(markup: str) -> None:
    """Render self-contained HTML without Markdown escaping."""
    st.html(dedent(markup).strip())


def metric_card(
    label: str,
    value: str,
    change: float,
    icon_name: str = "activity",
    tone: str = "primary",
    period: str = "vs last period",
) -> None:
    """Render a KPI metric card."""
    colors = ThemeEngine.active_colors()
    trend = "up" if change > 0 else "down" if change < 0 else "neutral"
    trend_icon = "trending-up" if change > 0 else "trending-down" if change < 0 else "minus"
    _html(
        f"""
        <div class="if-metric-card if-fade-in if-hover-lift">
            <div class="if-metric-top">
                <span class="if-metric-label">{label}</span>
                <div class="if-card-icon {tone}">{icon(icon_name, 18, colors.get(tone, colors['primary']))}</div>
            </div>
            <div class="if-metric-value">{value}</div>
            <div class="if-metric-footer">
                <span class="if-trend-pill {trend}">
                    {icon(trend_icon, 12, 'currentColor')} {format_percent(change)}
                </span>
                <span class="if-caption">Updated just now</span>
            </div>
        </div>
        """
    )


def metric_grid(kpis: list[dict[str, Any]], columns: int = 4) -> None:
    """Render a responsive grid of KPI cards with drill-down functionality."""
    cols = st.columns(columns)
    
    @st.dialog("KPI Analysis", width="large")
    def analyze_kpi(label: str):
        st.write(f"Detailed historical trend for **{label}**")
        import pandas as pd
        import numpy as np
        import plotly.express as px
        df = pd.DataFrame({
            "Date": pd.date_range(start="2023-01-01", periods=30),
            "Value": np.random.randn(30).cumsum() + 100
        })
        fig = px.area(df, x="Date", y="Value", title=f"{label} (Last 30 Days)", color_discrete_sequence=["#6366f1"])
        st.plotly_chart(fig, use_container_width=True)
        
    for i, kpi in enumerate(kpis):
        with cols[i % columns]:
            metric_card(
                label=kpi["label"],
                value=kpi["value"],
                change=kpi["change"],
                icon_name=kpi.get("icon", "activity"),
                tone=kpi.get("tone", "primary"),
            )
            if st.button("Analyze", key=f"analyze_btn_{i}_{kpi['label']}", use_container_width=True):
                analyze_kpi(kpi["label"])


def section_header(title: str, subtitle: str = "", action_label: str = "") -> None:
    """Render a section header."""
    action_html = f'<span class="if-btn if-btn-ghost">{action_label}</span>' if action_label else ""
    sub_html = f'<div class="if-caption">{subtitle}</div>' if subtitle else ""
    _html(
        f"""
        <div class="if-section-header">
            <div>
                <div class="if-section-title">{title}</div>
                {sub_html}
            </div>
            {action_html}
        </div>
        """
    )


def card_start(title: str, subtitle: str = "", icon_name: str = "", tone: str = "primary") -> None:
    """Open a card container."""
    colors = ThemeEngine.active_colors()
    icon_html = ""
    if icon_name:
        icon_html = f'<div class="if-card-icon {tone}">{icon(icon_name, 18, colors.get(tone, colors["primary"]))}</div>'
    st.markdown(
        f"""
        <div class="if-card if-fade-in">
            <div class="if-card-header">
                <div>
                    <div class="if-card-title">{title}</div>
                    {"<div class='if-card-subtitle'>" + subtitle + "</div>" if subtitle else ""}
                </div>
                {icon_html}
            </div>
        """,
        unsafe_allow_html=True,
    )


def card_end() -> None:
    """Close a card container."""
    st.markdown("</div>", unsafe_allow_html=True)


def hero_section(greeting: str, subtitle: str, actions: list[tuple[str, str]] | None = None) -> None:
    """Render dashboard hero banner."""
    actions = actions or []
    actions_html = "".join(
        f'<span class="if-btn {"if-btn-ai" if i == 1 else "if-btn-primary" if i == 0 else "if-btn-secondary"}">{icon(a[1], 14, "currentColor")} {a[0]}</span>'
        for i, a in enumerate(actions)
    )
    _html(
        f"""
        <div class="if-hero if-fade-in">
            <div class="if-hero-copy" style="max-width: 620px; position: relative; z-index: 1;">
                <div class="if-badge primary" style="margin-bottom: 10px;">AI Business Intelligence</div>
                <div class="if-hero-greeting">{greeting}</div>
                <div class="if-hero-sub">Analyze customers. Predict revenue. Grow smarter.</div>
                <div class="if-hero-sub" style="margin-top: 10px;">{subtitle}</div>
                <div class="if-hero-sub" style="margin-top: 14px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <span class="if-tag">3 high-priority opportunities</span>
                    <span class="if-tag">2 churn risks</span>
                    <span class="if-tag">+12.6% forecast lift</span>
                </div>
            </div>
            <div class="if-hero-side" style="position: relative; z-index: 1; min-width: 240px;">
                <div class="if-card" style="padding: 16px 18px; min-width: 220px;">
                    <div class="if-caption">This month</div>
                    <div class="if-h2" style="margin-top: 4px;">₹2.48M</div>
                    <div class="if-badge success" style="margin-top: 8px;">+14.2% vs last month</div>
                </div>
                <div class="if-quick-actions" style="margin-top: 12px;">{actions_html}</div>
            </div>
        </div>
        """
    )


def insight_card(title: str, body: str) -> None:
    """Render an AI insight card."""
    _html(
        f"""
        <div class="if-insight-card">
            <div class="if-insight-title">{icon('sparkles', 14, 'var(--if-primary)')} {title}</div>
            <div class="if-insight-body">{body}</div>
        </div>
        """
    )


def alert_banner(level: str, title: str, message: str) -> None:
    """Render an alert banner."""
    icon_map = {"warning": "alert-triangle", "danger": "alert-circle", "info": "activity", "success": "check-circle"}
    _html(
        f"""
        <div class="if-alert {level}">
            {icon(icon_map.get(level, 'alert-circle'), 18, 'currentColor')}
            <div><strong>{title}</strong><br><span style="opacity:0.85">{message}</span></div>
        </div>
        """
    )


def timeline(items: list[dict[str, Any]]) -> None:
    """Render an activity timeline."""
    entries = ""
    for item in items:
        t = item.get("time")
        time_str = relative_time(t) if hasattr(t, "year") else str(t)
        entries += dedent(
            f"""
        <div class="if-timeline-item">
            <div class="if-timeline-time">{time_str}</div>
            <div class="if-timeline-text">{item.get('text', item.get('event', ''))}</div>
        </div>
        """
        )
    _html(f'<div class="if-timeline">{entries}</div>')


def empty_state(title: str, description: str, icon_name: str = "inbox", action: str = "") -> None:
    """Render an empty state."""
    action_html = f'<div style="margin-top:16px"><span class="if-btn if-btn-primary">{action}</span></div>' if action else ""
    _html(
        f"""
        <div class="if-empty-state">
            <div class="if-empty-icon">{icon(icon_name, 28, 'var(--if-text-muted)')}</div>
            <div class="if-empty-title">{title}</div>
            <div class="if-empty-desc">{description}</div>
            {action_html}
        </div>
        """
    )


def error_state(code: str, title: str, description: str, icon_name: str = "alert-circle") -> None:
    """Render an error state."""
    _html(
        f"""
        <div class="if-error-state">
            <div class="if-error-code">{code}</div>
            <div class="if-empty-icon" style="margin:16px auto">{icon(icon_name, 32, 'var(--if-danger)')}</div>
            <div class="if-empty-title">{title}</div>
            <div class="if-empty-desc">{description}</div>
        </div>
        """
    )


def badge(text: str, tone: str = "neutral") -> str:
    """Return badge HTML."""
    return f'<span class="if-badge {tone}">{text}</span>'


def tag(text: str) -> str:
    """Return tag HTML."""
    return f'<span class="if-tag">{text}</span>'


def status_indicator(label: str, status: str = "online") -> None:
    """Render online/offline status."""
    _html(f'<span class="if-status"><span class="if-status-dot {status}"></span>{label}</span>')


def progress_bar(value: float, label: str = "") -> None:
    """Render a labeled progress bar."""
    label_html = f'<div class="if-caption" style="margin-bottom:6px">{label}</div>' if label else ""
    _html(
        f"""
        {label_html}
        <div class="if-progress"><div class="if-progress-bar" style="width:{min(value, 100)}%"></div></div>
        """
    )


def custom_tabs(labels: list[str], key: str = "tabs") -> int:
    """Render custom tab bar; returns selected index via session state."""
    state_key = f"if_tab_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = 0
    cols = st.columns(len(labels))
    for i, label in enumerate(labels):
        with cols[i]:
            if st.button(label, key=f"{state_key}_{i}", use_container_width=True):
                st.session_state[state_key] = i
    active = st.session_state[state_key]
    tabs_html = "".join(
        f'<span class="if-tab {"active" if i == active else ""}">{lbl}</span>'
        for i, lbl in enumerate(labels)
    )
    _html(f'<div class="if-tabs">{tabs_html}</div>')
    return active


def chat_interface(messages: list[dict[str, str]], suggestions: list[str] | None = None) -> None:
    """Render AI chat UI."""
    bubbles = ""
    for msg in messages:
        role = msg.get("role", "ai")
        bubbles += f'<div class="if-chat-bubble {role}">{msg["content"]}</div>'
    sugg_html = ""
    if suggestions:
        chips = "".join(f'<span class="if-suggestion-chip">{s}</span>' for s in suggestions)
        sugg_html = f'<div class="if-chat-suggestions">{chips}</div>'
    _html(
        f"""
        <div class="if-chat-container">
            <div class="if-chat-messages">{bubbles}</div>
            {sugg_html}
        </div>
        """
    )


def data_table_html(df, columns: list[str] | None = None) -> str:
    """Build styled HTML table from DataFrame."""
    columns = columns or list(df.columns)
    header = "".join(f"<th>{c.replace('_', ' ').title()}</th>" for c in columns)
    rows = ""
    for _, row in df.iterrows():
        cells = "".join(f"<td>{row[c]}</td>" for c in columns)
        rows += f"<tr>{cells}</tr>"
    return f'<div class="if-table-wrap"><table class="if-data-table"><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table></div>'


def skeleton_loader(type: str = "chart") -> None:
    """Render a skeleton loader animation."""
    if type == "chart":
        _html(
            """
            <div class="if-card" style="padding: 24px;">
                <div class="if-skeleton if-skeleton-title"></div>
                <div class="if-skeleton if-skeleton-chart"></div>
            </div>
            """
        )
    elif type == "metric":
        _html(
            """
            <div class="if-card" style="padding: 16px;">
                <div class="if-skeleton if-skeleton-text" style="width: 40%"></div>
                <div class="if-skeleton if-skeleton-title" style="margin-top:12px; margin-bottom:8px; height: 32px; width: 60%"></div>
                <div class="if-skeleton if-skeleton-text" style="width: 80%"></div>
            </div>
            """
        )
    else:
        _html(
            """
            <div class="if-card" style="padding: 24px;">
                <div class="if-skeleton if-skeleton-title"></div>
                <div class="if-skeleton if-skeleton-text"></div>
                <div class="if-skeleton if-skeleton-text" style="width: 90%"></div>
                <div class="if-skeleton if-skeleton-text" style="width: 80%"></div>
            </div>
            """
        )


def status_badge(text: str, tone: str = "success", live: bool = True) -> str:
    """Return HTML for a status badge with an optional live pulse dot."""
    dot_html = f'<span class="if-pulse-dot {tone}"></span>' if live else ""
    return f'<div class="if-badge {tone}" style="display:inline-flex; align-items:center; gap:6px;">{dot_html}<span>{text}</span></div>'


def action_prompt_chips(suggestions: list[str]) -> None:
    """Render interactive AI prompt suggestion chips."""
    chips = "".join(f'<div class="if-action-chip">✨ {s}</div>' for s in suggestions)
    _html(f'<div class="if-chip-container">{chips}</div>')

