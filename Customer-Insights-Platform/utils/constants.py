"""InsightForge AI — design tokens and application constants."""

from __future__ import annotations

APP_NAME = "OmniMall AI"
APP_TAGLINE = "Intelligent Retail Management for Malls"
APP_VERSION = "1.0.0"

# ── Color system (light theme defaults; dark overrides in theme.py) ──────────
COLORS_LIGHT = {
    "primary": "#4F46E5",
    "primary_hover": "#4338CA",
    "primary_subtle": "#EEF2FF",
    "secondary": "#7C3AED",
    "secondary_hover": "#6D28D9",
    "accent": "#2563EB",
    "accent_subtle": "#DBEAFE",
    "success": "#22C55E",
    "success_subtle": "#DCFCE7",
    "warning": "#F59E0B",
    "warning_subtle": "#FEF3C7",
    "danger": "#EF4444",
    "danger_subtle": "#FEE2E2",
    "info": "#2563EB",
    "info_subtle": "#DBEAFE",
    "neutral_50": "#F8FAFC",
    "neutral_100": "#F4F7FC",
    "neutral_200": "#E5E7EB",
    "neutral_300": "#CBD5E1",
    "neutral_400": "#94A3B8",
    "neutral_500": "#6B7280",
    "neutral_600": "#475569",
    "neutral_700": "#334155",
    "neutral_800": "#1E293B",
    "neutral_900": "#111827",
    "background": "#F4F7FC",
    "background_alt": "#FFFFFF",
    "card": "#FFFFFF",
    "card_hover": "#F8FAFC",
    "sidebar": "#111827",
    "sidebar_border": "#1F2937",
    "text_primary": "#111827",
    "text_secondary": "#6B7280",
    "text_muted": "#94A3B8",
    "border": "#E5E7EB",
    "border_strong": "#CBD5E1",
    "chart_1": "#4F46E5",
    "chart_2": "#2563EB",
    "chart_3": "#7C3AED",
    "chart_4": "#22C55E",
    "chart_5": "#F59E0B",
    "chart_6": "#EF4444",
    "hover": "rgba(79, 70, 229, 0.08)",
    "disabled": "#CBD5E1",
    "focus": "#4F46E5",
    "glass": "rgba(255, 255, 255, 0.78)",
    "shadow": "rgba(17, 24, 39, 0.08)",
}

COLORS_DARK = {
    "primary": "#6366F1",
    "primary_hover": "#818CF8",
    "primary_subtle": "#1E1B4B",
    "secondary": "#8B5CF6",
    "secondary_hover": "#A78BFA",
    "accent": "#3B82F6",
    "accent_subtle": "#172554",
    "success": "#34D399",
    "success_subtle": "#064E3B",
    "warning": "#FBBF24",
    "warning_subtle": "#78350F",
    "danger": "#F87171",
    "danger_subtle": "#7F1D1D",
    "info": "#60A5FA",
    "info_subtle": "#1E3A8A",
    "neutral_50": "#0F172A",
    "neutral_100": "#111827",
    "neutral_200": "#1F2937",
    "neutral_300": "#374151",
    "neutral_400": "#4B5563",
    "neutral_500": "#6B7280",
    "neutral_600": "#9CA3AF",
    "neutral_700": "#D1D5DB",
    "neutral_800": "#E5E7EB",
    "neutral_900": "#F9FAFB",
    "background": "#0B1120",
    "background_alt": "#111827",
    "card": "#151D2E",
    "card_hover": "#1A2332",
    "sidebar": "#111827",
    "sidebar_border": "#1F2937",
    "text_primary": "#F9FAFB",
    "text_secondary": "#D1D5DB",
    "text_muted": "#9CA3AF",
    "border": "#1F2937",
    "border_strong": "#374151",
    "chart_1": "#6366F1",
    "chart_2": "#3B82F6",
    "chart_3": "#8B5CF6",
    "chart_4": "#34D399",
    "chart_5": "#FBBF24",
    "chart_6": "#F87171",
    "hover": "rgba(99, 102, 241, 0.14)",
    "disabled": "#4B5563",
    "focus": "#6366F1",
    "glass": "rgba(17, 24, 39, 0.86)",
    "shadow": "rgba(0, 0, 0, 0.35)",
}

# ── Typography ───────────────────────────────────────────────────────────────
FONT_FAMILY = "'Plus Jakarta Sans', 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif"
FONT_DISPLAY = "2.25rem"
FONT_H1 = "1.875rem"
FONT_H2 = "1.5rem"
FONT_H3 = "1.25rem"
FONT_H4 = "1.125rem"
FONT_BODY = "0.9375rem"
FONT_CAPTION = "0.8125rem"
FONT_LABEL = "0.75rem"
FONT_KPI = "1.75rem"

# ── Spacing (rem) ────────────────────────────────────────────────────────────
SPACE_XS = "0.25rem"
SPACE_SM = "0.5rem"
SPACE_MD = "1rem"
SPACE_LG = "1.5rem"
SPACE_XL = "2rem"
SPACE_2XL = "3rem"
SPACE_3XL = "4rem"

# ── Border radius ────────────────────────────────────────────────────────────
RADIUS_SM = "6px"
RADIUS_MD = "10px"
RADIUS_LG = "14px"
RADIUS_XL = "20px"
RADIUS_FULL = "9999px"

# ── Shadows ──────────────────────────────────────────────────────────────────
SHADOW_SM = "0 1px 2px var(--if-shadow)"
SHADOW_MD = "0 4px 12px var(--if-shadow)"
SHADOW_LG = "0 8px 24px var(--if-shadow)"
SHADOW_CARD = "0 1px 3px var(--if-shadow), 0 1px 2px -1px var(--if-shadow)"

# ── Layout ───────────────────────────────────────────────────────────────────
SIDEBAR_WIDTH = "280px"
SIDEBAR_COLLAPSED = "72px"
TOPBAR_HEIGHT = "64px"
MAX_CONTENT_WIDTH = "1440px"

CHART_PALETTE = [
    COLORS_LIGHT["chart_1"],
    COLORS_LIGHT["chart_2"],
    COLORS_LIGHT["chart_3"],
    COLORS_LIGHT["chart_4"],
    COLORS_LIGHT["chart_5"],
    COLORS_LIGHT["chart_6"],
]
