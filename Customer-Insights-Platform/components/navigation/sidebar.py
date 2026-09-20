"""Sidebar navigation for InsightForge AI."""

from __future__ import annotations

from textwrap import dedent

import streamlit as st

from utils.constants import APP_NAME, APP_TAGLINE
from utils.icons import icon
from utils.navigation import get_role_nav_sections


def render_sidebar(active_nav: str) -> None:
    """Render branded sidebar with Streamlit page links."""
    collapsed = st.session_state.get("if_sidebar_collapsed", False)

    nav_sections = get_role_nav_sections(st.session_state.get("if_user_role", "Admin"))
    user_name = st.session_state.get("if_user_name", "Alex Morgan")
    user_role = st.session_state.get("if_user_role", "Admin")
    role_group = st.session_state.get("if_user_role_group", "General")
    workspace = st.session_state.get("if_workspace", "Production")
    org = st.session_state.get("if_org_name", "Acme Corporation")
    initials = "".join(w[0] for w in user_name.split()[:2]).upper()

    brand_section = ""
    if not collapsed:
        brand_section = f"""
            <div class="if-brand-text">
                <div class="if-brand-name">{APP_NAME}</div>
                <div class="if-brand-tag">{APP_TAGLINE[:38]}…</div>
            </div>
        """

    meta_section = ""
    if not collapsed:
        meta_section = f"""
            <div class="if-sidebar-meta">
                <div class="if-workspace-pill">
                    {icon('building-2', 13, 'currentColor')}
                    <span class="if-ws-label">{workspace}</span>
                    <span class="if-ws-dot"></span>
                </div>
                <div class="if-workspace-pill if-role-pill-row">
                    {icon('shield-check', 13, 'currentColor')}
                    <span class="if-ws-label">{user_role}</span>
                    <span class="if-ws-sep">·</span>
                    <span class="if-ws-group">{role_group}</span>
                </div>
            </div>
        """

    toggle_icon = icon("chevrons-left", 14, "currentColor") if not collapsed else icon("chevrons-right", 14, "currentColor")
    toggle_label = "Collapse" if not collapsed else ""

    st.html(
        dedent(
            f"""
            <div class="if-sidebar-shell">
                <!-- Brand row -->
                <div class="if-sidebar-brand">
                    <div class="if-logo-mark">{icon('zap', 16, '#fff') if not collapsed else 'IF'}</div>
                    {brand_section}
                    <button class="if-collapse-btn" id="if_collapse_trigger"
                        title="{'Collapse sidebar' if not collapsed else 'Expand sidebar'}">
                        {toggle_icon}
                    </button>
                </div>
                {meta_section}
            </div>

            <style>
            /* ── Sidebar shell ── */
            .if-sidebar-shell {{
                background: var(--if-sidebar, linear-gradient(180deg,#1e1b4b,#1e3a5f));
                border: 1px solid var(--if-sidebar-border, rgba(255,255,255,0.08));
                border-radius: 16px;
                padding: 4px;
                margin-bottom: 6px;
                overflow: hidden;
            }}

            /* ── Brand row ── */
            .if-sidebar-brand {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 12px 10px;
                border-radius: 12px 12px 0 0;
            }}

            .if-logo-mark {{
                width: 38px;
                height: 38px;
                min-width: 38px;
                border-radius: 11px;
                background: linear-gradient(135deg, #6366f1 0%, #2563eb 100%);
                color: #fff;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 800;
                font-size: 14px;
                letter-spacing: -0.03em;
                box-shadow: 0 4px 14px rgba(99,102,241,0.4), inset 0 1px 0 rgba(255,255,255,0.2);
                flex-shrink: 0;
            }}

            .if-brand-text {{
                flex: 1;
                min-width: 0;
                overflow: hidden;
            }}

            .if-brand-name {{
                font-size: 14px;
                font-weight: 700;
                color: var(--if-text-primary);
                letter-spacing: -0.025em;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}

            .if-brand-tag {{
                font-size: 10.5px;
                color: var(--if-text-muted);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                margin-top: 1px;
                opacity: 0.75;
            }}

            /* ── Collapse toggle ── */
            .if-collapse-btn {{
                display: flex;
                align-items: center;
                justify-content: center;
                width: 28px;
                height: 28px;
                min-width: 28px;
                border-radius: 8px;
                border: 1px solid rgba(229,231,235,0.5);
                background: rgba(255,255,255,0.55);
                color: var(--if-text-muted);
                cursor: pointer;
                transition: all 0.18s ease;
                flex-shrink: 0;
                padding: 0;
            }}

            .if-collapse-btn:hover {{
                background: rgba(99,102,241,0.1);
                border-color: rgba(99,102,241,0.4);
                color: #6366f1;
                transform: scale(1.06);
            }}

            /* ── Meta pills ── */
            .if-sidebar-meta {{
                display: flex;
                flex-direction: column;
                gap: 5px;
                padding: 0 10px 10px;
            }}

            .if-workspace-pill {{
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 6px 10px;
                border-radius: 8px;
                background: rgba(255,255,255,0.72);
                border: 1px solid rgba(229,231,235,0.9);
                font-size: 12px;
                font-weight: 500;
                color: var(--if-text-secondary);
                box-shadow: inset 0 1px 1px rgba(255,255,255,0.85), 0 1px 3px rgba(15,23,42,0.04);
                overflow: hidden;
                white-space: nowrap;
            }}

            .if-ws-label {{
                font-weight: 600;
                color: var(--if-text-primary);
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}

            .if-ws-sep {{
                color: var(--if-text-muted);
                opacity: 0.5;
                flex-shrink: 0;
            }}

            .if-ws-group {{
                color: var(--if-text-muted);
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                font-size: 11px;
            }}

            .if-ws-dot {{
                width: 6px;
                height: 6px;
                min-width: 6px;
                background: #10b981;
                border-radius: 50%;
                margin-left: auto;
                box-shadow: 0 0 0 2px rgba(16,185,129,0.2);
            }}

            /* ── Scrollable nav region ── */
            section[data-testid="stSidebar"] > div:first-child {{
                overflow-y: auto !important;
                overflow-x: hidden !important;
                scrollbar-width: thin;
                scrollbar-color: rgba(99,102,241,0.28) transparent;
                padding-right: 2px;
            }}

            section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar {{
                width: 4px;
            }}
            section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-track {{
                background: transparent;
                margin: 12px 0;
            }}
            section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb {{
                background: rgba(99,102,241,0.28);
                border-radius: 999px;
                transition: background 0.2s ease;
            }}
            section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb:hover {{
                background: rgba(99,102,241,0.52);
            }}

            /* ── Resize handle ── */
            #if-resize-handle {{
                position: fixed;
                top: 10px;
                left: calc(var(--if-sidebar-w, 272px) + 10px - 6px);
                width: 12px;
                height: calc(100vh - 20px);
                cursor: col-resize;
                z-index: 1100;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 0 8px 8px 0;
                transition: background 0.2s ease, left 0.01s linear;
            }}

            #if-resize-handle::before {{
                content: '';
                display: block;
                width: 3px;
                height: 48px;
                border-radius: 999px;
                background: rgba(99,102,241,0.18);
                transition: background 0.2s ease, height 0.2s ease;
            }}

            #if-resize-handle:hover::before,
            #if-resize-handle.dragging::before {{
                background: rgba(99,102,241,0.55);
                height: 64px;
            }}

            #if-resize-handle .if-resize-arrow {{
                position: absolute;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 1px;
                opacity: 0;
                transition: opacity 0.2s ease;
                pointer-events: none;
            }}

            #if-resize-handle:hover .if-resize-arrow,
            #if-resize-handle.dragging .if-resize-arrow {{
                opacity: 1;
            }}

            /* ── Nav section labels ── */
            .if-nav-label {{
                font-size: 9.5px;
                font-weight: 700;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                color: var(--if-text-muted);
                padding: 14px 12px 5px;
                opacity: 0.65;
                user-select: none;
            }}

            /* ── Page links ── */
            div[data-testid="stPageLink"] {{
                margin-bottom: 1px;
            }}

            div[data-testid="stPageLink"] a {{
                font-size: 13px !important;
                font-weight: 500 !important;
                padding: 8px 12px !important;
                border-radius: 10px !important;
                color: var(--if-text-secondary) !important;
                transition: all 0.15s ease !important;
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }}

            div[data-testid="stPageLink"] a:hover {{
                background: var(--if-hover) !important;
                color: var(--if-text-primary) !important;
                padding-left: 14px !important;
            }}

            div[data-testid="stPageLink"] a[aria-current="page"],
            div[data-testid="stPageLink"] a.active {{
                background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(37,99,235,0.08)) !important;
                color: #6366f1 !important;
                font-weight: 600 !important;
                border: 1px solid rgba(99,102,241,0.18) !important;
            }}

            /* ── Collapse button (Streamlit native) override ── */
            div[data-testid="stButton"] button[kind="secondary"] {{
                width: 100% !important;
                border-radius: 10px !important;
                border: 1px solid rgba(229,231,235,0.85) !important;
                background: rgba(255,255,255,0.7) !important;
                color: var(--if-text-secondary) !important;
                font-size: 12.5px !important;
                font-weight: 600 !important;
                padding: 7px 14px !important;
                letter-spacing: 0.01em !important;
                box-shadow: 0 1px 4px rgba(15,23,42,0.06) !important;
                transition: all 0.18s ease !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 6px !important;
            }}

            div[data-testid="stButton"] button[kind="secondary"]:hover {{
                background: rgba(99,102,241,0.08) !important;
                border-color: rgba(99,102,241,0.3) !important;
                color: #6366f1 !important;
                transform: none !important;
            }}
            </style>

            <!-- Resize handle injected into parent document via JS -->
            <script>
            (function() {{
                // Avoid double-init on Streamlit re-renders
                if (document.getElementById('if-resize-handle')) return;

                const MIN_W = 180;
                const MAX_W = 480;
                const CSS_VAR = '--if-sidebar-w';
                const STORAGE_KEY = 'if_sidebar_width';

                // Read persisted width
                let currentW = parseInt(localStorage.getItem(STORAGE_KEY)) ||
                               parseInt(getComputedStyle(document.documentElement).getPropertyValue(CSS_VAR)) ||
                               272;
                currentW = Math.max(MIN_W, Math.min(MAX_W, currentW));

                function applySidebarWidth(w) {{
                    document.documentElement.style.setProperty(CSS_VAR, w + 'px');
                    // Update Streamlit's sidebar element directly
                    const sb = document.querySelector('section[data-testid="stSidebar"]');
                    if (sb) {{
                        sb.style.width = w + 'px';
                        sb.style.minWidth = w + 'px';
                        sb.style.maxWidth = w + 'px';
                    }}
                    // Shift main content
                    const main = document.querySelector('.if-main') ||
                                 document.querySelector('section[data-testid="stMain"]');
                    if (main) main.style.marginLeft = (w + 20) + 'px';
                    // Reposition handle
                    const handle = document.getElementById('if-resize-handle');
                    if (handle) handle.style.left = (w + 10 - 6) + 'px';
                }}

                // Apply on load
                applySidebarWidth(currentW);

                // Create handle element in the top-level document
                const handle = document.createElement('div');
                handle.id = 'if-resize-handle';
                handle.title = 'Drag to resize sidebar';
                // Double-arrow icon
                handle.innerHTML = `
                    <span class="if-resize-arrow" style="
                        position:absolute; display:flex; flex-direction:row;
                        align-items:center; gap:1px; opacity:0; transition:opacity 0.2s;
                        pointer-events:none; top:50%; transform:translateY(-50%);
                        font-size:11px; color:#6366f1; font-weight:700; letter-spacing:-1px;
                    ">↔</span>
                `;
                document.body.appendChild(handle);

                // Show arrow on hover
                handle.addEventListener('mouseenter', () => {{
                    handle.querySelector('.if-resize-arrow').style.opacity = '1';
                }});
                handle.addEventListener('mouseleave', () => {{
                    if (!handle.classList.contains('dragging'))
                        handle.querySelector('.if-resize-arrow').style.opacity = '0';
                }});

                // Drag logic
                let dragging = false;
                let startX = 0;
                let startW = 0;

                handle.addEventListener('pointerdown', (e) => {{
                    dragging = true;
                    startX = e.clientX;
                    startW = currentW;
                    handle.classList.add('dragging');
                    handle.querySelector('.if-resize-arrow').style.opacity = '1';
                    document.body.style.cursor = 'col-resize';
                    document.body.style.userSelect = 'none';
                    handle.setPointerCapture(e.pointerId);
                }});

                handle.addEventListener('pointermove', (e) => {{
                    if (!dragging) return;
                    const delta = e.clientX - startX;
                    const newW = Math.max(MIN_W, Math.min(MAX_W, startW + delta));
                    currentW = newW;
                    applySidebarWidth(newW);
                }});

                handle.addEventListener('pointerup', () => {{
                    if (!dragging) return;
                    dragging = false;
                    handle.classList.remove('dragging');
                    handle.querySelector('.if-resize-arrow').style.opacity = '0';
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    localStorage.setItem(STORAGE_KEY, currentW);
                }});
            }})();
            </script>
            """
        )
    )

    # Collapse/Expand button
    toggle_text = "⟨  Collapse" if not collapsed else "⟩"
    if st.button(toggle_text, key="if_toggle_sidebar", use_container_width=True):
        st.session_state["if_sidebar_collapsed"] = not collapsed
        st.rerun()

    if not collapsed:
        # Global Search
        from utils.navigation import all_nav_items
        all_items = all_nav_items()
        search_options = [""] + [item.label for item in all_items]
        
        search_val = st.selectbox(
            "Search",
            options=search_options,
            label_visibility="collapsed",
            placeholder="🔍 Search or jump to...",
            index=0
        )
        if search_val:
            for item in all_items:
                if item.label == search_val:
                    # Clear search selection to avoid looping
                    st.switch_page(item.page)
                    break
        
        # Theme Toggle
        from utils.theme import ThemeEngine
        current_theme = ThemeEngine.get_mode()
        st.write("") # spacer
        st.html('<div class="if-nav-label" style="padding-top:0;">THEME</div>')
        theme_cols = st.columns(3)
        if theme_cols[0].button("🌞 Light", use_container_width=True, type="primary" if current_theme == "light" else "secondary"):
            ThemeEngine.set_mode("light")
            st.rerun()
        if theme_cols[1].button("🌙 Dark", use_container_width=True, type="primary" if current_theme == "dark" else "secondary"):
            ThemeEngine.set_mode("dark")
            st.rerun()
        if theme_cols[2].button("💻 Auto", use_container_width=True, type="primary" if current_theme == "auto" else "secondary"):
            ThemeEngine.set_mode("auto")
            st.rerun()
        st.write("") # spacer

    # Nav sections
    for section in nav_sections:
        if not collapsed:
            st.html(f'<div class="if-nav-label">{section.title}</div>')
        for item in section.items:
            is_active = item.id == active_nav
            prefix = "● " if is_active else ""
            label = item.label if not collapsed else item.label[:3].upper()
            st.page_link(item.page, label=f"{prefix}{label}")

    # Footer environment / AI status strip
    if not collapsed:
        st.html(
            dedent(
                f"""
                <div class="if-sidebar-footer-strip">
                    <div class="if-footer-pill">
                        {icon('cpu', 12, 'currentColor')}
                        <span>Development</span>
                    </div>
                    <div class="if-footer-pill ai">
                        {icon('sparkles', 12, '#6366f1')}
                        <span>AI Ready</span>
                        <span class="if-ai-dot"></span>
                    </div>
                </div>
                <style>
                .if-sidebar-footer-strip {{
                    margin-top: 12px;
                    padding: 10px 10px 6px;
                    border-top: 1px solid var(--if-border);
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                }}
                .if-footer-pill {{
                    display: flex;
                    align-items: center;
                    gap: 7px;
                    padding: 6px 10px;
                    border-radius: 8px;
                    background: rgba(255,255,255,0.65);
                    border: 1px solid rgba(229,231,235,0.8);
                    font-size: 11.5px;
                    font-weight: 500;
                    color: var(--if-text-secondary);
                    white-space: nowrap;
                    overflow: hidden;
                }}
                .if-footer-pill.ai {{
                    background: linear-gradient(135deg, rgba(99,102,241,0.07), rgba(37,99,235,0.04));
                    border-color: rgba(99,102,241,0.18);
                    color: #6366f1;
                    font-weight: 600;
                }}
                .if-ai-dot {{
                    width: 6px;
                    height: 6px;
                    min-width: 6px;
                    background: #10b981;
                    border-radius: 50%;
                    margin-left: auto;
                    animation: if-ai-pulse 2.4s ease-in-out infinite;
                    box-shadow: 0 0 0 2px rgba(16,185,129,0.2);
                }}
                @keyframes if-ai-pulse {{
                    0%, 100% {{ opacity: 1; transform: scale(1); }}
                    50% {{ opacity: 0.65; transform: scale(0.85); }}
                }}
                </style>
                """
            )
        )
