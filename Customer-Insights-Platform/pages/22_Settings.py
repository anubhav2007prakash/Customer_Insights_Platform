"""Settings — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.ui.cards import alert_banner, hero_section, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.theme import ThemeEngine


def render_profile_tab() -> None:
    """Render the Profile settings tab."""
    section_header("Profile settings", "The identity and contact details your team sees")
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Full name", value=st.session_state.get("if_user_name", "Alex Morgan"))
            email = st.text_input("Email", value=st.session_state.get("if_user_email", "alex.morgan@acmecorp.com"))
        with c2:
            job_title = st.text_input("Job title", value=st.session_state.get("if_user_title", "VP of Analytics"))
            phone = st.text_input("Phone", value=st.session_state.get("if_user_phone", "+1 (555) 123-4567"))
        saved = st.form_submit_button("Save Profile", type="primary", use_container_width=True)
        if saved:
            st.session_state["if_user_name"] = full_name
            st.session_state["if_user_email"] = email
            st.session_state["if_user_title"] = job_title
            st.session_state["if_user_phone"] = phone
            st.success("Profile saved successfully.")


def render_workspace_tab() -> None:
    """Render the Workspace settings tab."""
    section_header("Workspace", "Default operating context for daily work")
    with st.form("workspace_form"):
        org = st.text_input("Organization", value=st.session_state.get("if_org_name", "Acme Corporation"))
        workspace = st.selectbox(
            "Default workspace",
            ["Production", "Staging", "Development"],
            index=["Production", "Staging", "Development"].index(
                st.session_state.get("if_workspace", "Production")
            ),
        )
        tz = st.selectbox(
            "Timezone",
            ["UTC", "America/New_York", "Europe/London", "Asia/Singapore"],
            index=["UTC", "America/New_York", "Europe/London", "Asia/Singapore"].index(
                st.session_state.get("if_user_timezone", "UTC")
            ),
        )
        saved = st.form_submit_button("Save Workspace Settings", type="primary", use_container_width=True)
        if saved:
            st.session_state["if_org_name"] = org
            st.session_state["if_workspace"] = workspace
            st.session_state["if_user_timezone"] = tz
            st.success("Workspace settings saved.")


def render_security_tab() -> None:
    """Render the Security settings tab."""
    section_header("Security", "Keep the platform secure without slowing teams down")
    with st.form("security_form"):
        current_pw = st.text_input("Current password", type="password")
        new_pw = st.text_input("New password", type="password")
        confirm_pw = st.text_input("Confirm new password", type="password")
        tfa = st.checkbox(
            "Enable two-factor authentication",
            value=st.session_state.get("if_tfa_enabled", False),
        )
        sso = st.checkbox(
            "Require SSO for all users",
            value=st.session_state.get("if_sso_enabled", False),
        )
        submitted = st.form_submit_button("Update Security", type="primary", use_container_width=True)
        if submitted:
            if new_pw and new_pw != confirm_pw:
                st.error("New password and confirmation do not match.")
            elif new_pw and len(new_pw) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                if new_pw:
                    st.session_state["if_user_password"] = new_pw
                st.session_state["if_tfa_enabled"] = tfa
                st.session_state["if_sso_enabled"] = sso
                st.success("Security settings updated.")


def render_theme_tab() -> None:
    """Render the Theme preferences tab."""
    section_header("Theme & Display Preferences", "Customize appearance, primary accent colors, and dashboard widget layout")
    tc1, tc2 = st.columns(2)
    with tc1:
        theme = st.radio(
            "Appearance Mode",
            ["light", "dark", "auto"],
            index=["light", "dark", "auto"].index(ThemeEngine.get_mode()),
            horizontal=True,
        )
        accent_color = st.selectbox(
            "Primary Accent Color",
            ["Indigo (#6366f1)", "Emerald (#10b981)", "Violet (#8b5cf6)", "Cyan (#06b6d4)", "Amber (#f59e0b)"],
            index=["Indigo (#6366f1)", "Emerald (#10b981)", "Violet (#8b5cf6)", "Cyan (#06b6d4)", "Amber (#f59e0b)"].index(
                st.session_state.get("if_accent_color", "Indigo (#6366f1)")
            ),
        )
    with tc2:
        density = st.radio(
            "Layout Density",
            ["Standard", "Compact"],
            index=["Standard", "Compact"].index(st.session_state.get("if_layout_density", "Standard")),
            horizontal=True,
        )
        reduce_motion = st.checkbox(
            "Reduce motion & animations",
            value=st.session_state.get("if_reduce_motion", False),
        )
        high_contrast = st.checkbox(
            "High contrast accessibility mode",
            value=st.session_state.get("if_high_contrast", False),
        )

    st.markdown("---")
    st.markdown("**Dashboard Widget Customization**")
    wc1, wc2, wc3 = st.columns(3)
    with wc1:
        show_kpi = st.checkbox("KPI Metric Strip", value=st.session_state.get("widget_show_kpi", True))
        show_trend = st.checkbox("Revenue Trend Chart", value=st.session_state.get("widget_show_trend", True))
    with wc2:
        show_map = st.checkbox("Floor Heatmap Matrix", value=st.session_state.get("widget_show_map", True))
        show_recs = st.checkbox("AI Recommendations Module", value=st.session_state.get("widget_show_recs", True))
    with wc3:
        show_churn = st.checkbox("Churn Watchlist Widget", value=st.session_state.get("widget_show_churn", True))
        show_activity = st.checkbox("Live Activity Feed", value=st.session_state.get("widget_show_activity", True))

    if st.button("Apply Theme & Display Preferences", type="primary", use_container_width=True):
        ThemeEngine.set_mode(theme)
        st.session_state["if_accent_color"] = accent_color
        st.session_state["if_layout_density"] = density
        st.session_state["if_reduce_motion"] = reduce_motion
        st.session_state["if_high_contrast"] = high_contrast
        st.session_state["widget_show_kpi"] = show_kpi
        st.session_state["widget_show_trend"] = show_trend
        st.session_state["widget_show_map"] = show_map
        st.session_state["widget_show_recs"] = show_recs
        st.session_state["widget_show_churn"] = show_churn
        st.session_state["widget_show_activity"] = show_activity
        st.success(f"Display preferences updated successfully.")
        st.rerun()



def render_notifications_tab() -> None:
    """Render the Notifications preferences tab."""
    section_header("Notification preferences", "Make sure alerts are useful and timely")
    with st.form("notifications_form"):
        email_notif = st.toggle("Email notifications", value=st.session_state.get("if_notif_email", True))
        push_notif = st.toggle("Push notifications", value=st.session_state.get("if_notif_push", True))
        digest = st.toggle("Weekly digest", value=st.session_state.get("if_notif_digest", True))
        ai_alerts = st.toggle("AI insight alerts", value=st.session_state.get("if_notif_ai", True))
        churn_alerts = st.toggle("Churn risk alerts", value=st.session_state.get("if_notif_churn", True))
        saved = st.form_submit_button("Save Notifications", type="primary", use_container_width=True)
        if saved:
            st.session_state["if_notif_email"] = email_notif
            st.session_state["if_notif_push"] = push_notif
            st.session_state["if_notif_digest"] = digest
            st.session_state["if_notif_ai"] = ai_alerts
            st.session_state["if_notif_churn"] = churn_alerts
            st.success("Notification preferences saved.")


def render_billing_tab() -> None:
    """Render the Billing tab."""
    section_header("Billing", "Your current plan and consumption")
    st.markdown("**Enterprise Plan** — $2,499/month")
    st.markdown("Next billing date: August 1, 2026")
    st.progress(0.72, text="Seats used: 18 / 25")
    if st.button("Manage Subscription", use_container_width=True):
        st.info("Subscription management is handled via your account portal.")


def render_api_keys_tab() -> None:
    """Render #17 API Key Manager with scope controls and revoke features."""
    section_header("🔑 API Key Manager", "Generate, scope, and manage API keys for programmatic access")

    api_keys = [
        {"name": "Production Server", "key": "if_live_sk_••••••••9a2f", "scope": "read_write", "created": "Jan 12, 2026", "last_used": "12m ago"},
        {"name": "Analytics Pipeline", "key": "if_live_sk_••••••••4f1b", "scope": "read_only",  "created": "Feb 04, 2026", "last_used": "2h ago"},
        {"name": "Staging Webhook",  "key": "if_test_sk_••••••••88cc", "scope": "admin",      "created": "Mar 01, 2026", "last_used": "3d ago"},
    ]

    for k in api_keys:
        st.html(
            f"""
            <div class="if-apikey-row">
                <span class="if-apikey-name">{k['name']}</span>
                <span class="if-apikey-value">{k['key']}</span>
                <span class="if-apikey-scope">{k['scope']}</span>
                <span style="font-size:11px; color:#6b7280;">Last used: {k['last_used']}</span>
            </div>
            """
        )

    with st.expander("➕ Generate New API Key", expanded=False):
        with st.form("new_api_key_form"):
            c1, c2 = st.columns(2)
            with c1:
                k_name = st.text_input("Key Name", placeholder="e.g. BI Dashboard Connector")
                k_scope = st.selectbox("Scope", ["read_only", "read_write", "admin"])
            with c2:
                k_exp = st.selectbox("Expiration", ["30 Days", "90 Days", "1 Year", "Never"])
            if st.form_submit_button("Generate Key", type="primary", use_container_width=True):
                import secrets
                raw_key = f"if_{'live' if k_scope!='test' else 'test'}_sk_{secrets.token_hex(16)}"
                st.success(f"Key created! Copy now: `{raw_key}` (Will not be displayed again)")


def render_shortcuts_tab() -> None:
    """Render #8 Keyboard Shortcuts helper panel."""
    section_header("⌨️ Keyboard Shortcuts", "Boost your productivity with global hotkeys")

    shortcuts = [
        {"desc": "Open Command Palette / Search", "keys": ["Ctrl", "K"]},
        {"desc": "Toggle Sidebar", "keys": ["Ctrl", "\\"]},
        {"desc": "Switch Light / Dark Theme", "keys": ["Ctrl", "Shift", "T"]},
        {"desc": "Quick Export Current Page", "keys": ["Ctrl", "E"]},
        {"desc": "Focus AI Assistant Input", "keys": ["Ctrl", "J"]},
        {"desc": "Go to Dashboard", "keys": ["G", "D"]},
        {"desc": "Go to Reports", "keys": ["G", "R"]},
    ]

    for s in shortcuts:
        st.html(
            f"""
            <div class="if-shortcut-row">
                <span>{s['desc']}</span>
                <div class="if-shortcut-keys">
                    {' '.join([f'<span class="if-kbd">{k}</span>' for k in s['keys']])}
                </div>
            </div>
            """
        )


def render_integrations_tab() -> None:
    """Render the Integrations tab."""
    section_header("Connected integrations", "Manage your integrations in one place")
    st.page_link("pages/19_Integrations.py", label="Manage Integrations →")


def render_help_section() -> None:
    """Render the Help & Feedback section."""
    st.markdown("---")
    section_header("Help & feedback", "Support and product feedback")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Help Center**")
        st.markdown("Documentation, guides, and tutorials")
        if st.button("Open Help Center", use_container_width=True):
            st.info("Opening help center documentation...")
    with c2:
        st.markdown("**Send Feedback**")
        feedback_text = st.text_area("Your feedback", placeholder="Tell us how we can improve…", label_visibility="collapsed", key="feedback_text")
        if st.button("Submit Feedback", type="primary", use_container_width=True):
            if feedback_text.strip():
                st.session_state["if_feedback_sent"] = True
                st.success("Thank you for your feedback!")
            else:
                st.warning("Please enter your feedback before submitting.")


def main() -> None:
    """Bootstrap and render the Settings page."""
    bootstrap_page(
        "Settings",
        "settings",
        breadcrumbs=["Organization", "Settings"],
        subtitle="Profile, workspace, security, billing, and preferences",
        icon="⚙️",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    hero_copy = {
        "Data Analyst": "Fine-tune the experience, data access, and collaboration settings that shape how analysis gets done.",
        "Data Scientist": "Fine-tune the experience, model access, and collaboration settings that shape how experimentation gets done.",
        "Manager": "Fine-tune the experience, delivery access, and collaboration settings that shape how decisions get made.",
        "Admin": "Fine-tune the experience, security posture, and collaboration settings that shape how the platform operates.",
    }

    hero_section(
        f"{dashboard_context['hero_title']} — settings",
        hero_copy.get(role, "Fine-tune the experience, security posture, and collaboration settings that shape how the platform operates."),
        [("Update profile", "user"), ("Review security", "shield")],
    )

    alert_banner("info", "Preferences ready", "Your current workspace settings are ready for review and adjustment.")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "Profile", "Workspace", "Security", "Theme", "Notifications", "Billing", "API Keys", "Integrations", "⌨️ Shortcuts",
    ])

    with tab1:
        render_profile_tab()
    with tab2:
        render_workspace_tab()
    with tab3:
        render_security_tab()
    with tab4:
        render_theme_tab()
    with tab5:
        render_notifications_tab()
    with tab6:
        render_billing_tab()
    with tab7:
        render_api_keys_tab()
    with tab8:
        render_integrations_tab()
    with tab9:
        render_shortcuts_tab()

    render_help_section()
    finish_page()


main()
