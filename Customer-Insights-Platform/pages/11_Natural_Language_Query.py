"""Natural Language Query — InsightForge AI."""

from __future__ import annotations

import streamlit as st

from components.charts.chart_factory import bar_chart, pie_chart
from components.ui.cards import alert_banner, hero_section, section_header
from utils.helpers import get_dashboard_context
from utils.page_bootstrap import bootstrap_page, finish_page
from utils.sample_data import get_top_products, get_traffic_sources


def render_suggestions(suggestions) -> None:
    """Render clickable question suggestion chips."""
    st.markdown("**Suggested questions**")
    cols = st.columns(3)
    for i, q in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(q, key=f"sug_{i}", use_container_width=True):
                st.session_state["nlq_query"] = q
                st.rerun()


def render_query_results(query: str, suggestions: list[str]) -> None:
    """Render query execution answers and visualizations (#14 NLP query -> chart)."""
    current_q = query or suggestions[0]
    q_lower = current_q.lower()

    st.markdown('<div class="if-card">', unsafe_allow_html=True)
    st.markdown(f"**Query:** {current_q}")

    if "churn" in q_lower or "retention" in q_lower:
        ans = "Customer retention is averaging **94.2%** for Enterprise accounts, while SMB churn risk has decreased by **2.1%** following recent loyalty campaign interventions."
    elif "top" in q_lower or "product" in q_lower:
        ans = "The top revenue generator is **Electronics & Gadgets** ($1.2M), followed by **Fashion & Apparel** ($840K) and **Beauty & Cosmetics** ($420K)."
    elif "traffic" in q_lower or "conversion" in q_lower:
        ans = "The **Loyalty App Push** channel yields the highest conversion rate at **7.8%**, outperforming organic search and social ads."
    else:
        ans = "Total footfall and tenant revenue last month reached **$2.4M**, representing a **12.4%** increase over the previous period."

    st.markdown(f"**AI Answer:** {ans}")
    st.markdown("</div>", unsafe_allow_html=True)

    section_header("Generated Visualization", f"Auto-selected chart for query: '{current_q[:35]}...'")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        if "churn" in q_lower or "retention" in q_lower:
            pie_chart(get_traffic_sources(), "source", "conversion", "Retention by Channel")
        else:
            bar_chart(get_top_products(), "product", "revenue", "Revenue Breakdown by Product Category", horizontal=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="if-card">', unsafe_allow_html=True)
        if "traffic" in q_lower or "conversion" in q_lower:
            pie_chart(get_traffic_sources(), "source", "sessions", "Traffic Sessions Distribution")
        else:
            bar_chart(get_top_products(), "product", "margin", "Profit Margin % by Category")
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Bootstrap and render NLQ page."""
    bootstrap_page(
        "Natural Language Query",
        "nlq",
        breadcrumbs=["AI", "Natural Language Query"],
        subtitle="Ask questions in plain English — get instant charts and answers",
        icon="💬",
    )

    role = st.session_state.get("if_user_role", "Admin")
    dashboard_context = get_dashboard_context(role)
    hero_copy = {
        "Data Analyst": "Turn plain English questions into quality-focused answers, charts, and follow-up recommendations.",
        "Data Scientist": "Turn plain English questions into experiment-focused answers, charts, and follow-up recommendations.",
        "Manager": "Turn plain English questions into delivery-focused answers, charts, and follow-up recommendations.",
        "Admin": "Turn plain English questions into governance-focused answers, charts, and follow-up recommendations.",
    }

    hero_section(
        f"{dashboard_context['hero_title']} — NLQ",
        hero_copy.get(role, "Turn plain English questions into instant business answers, charts, and follow-up recommendations."),
        [("Try a sample query", "message-square"), ("Open history", "history")],
    )

    alert_banner("success", "Query experience ready", "The assistant is ready to translate your next question into a clear insight.")

    suggestions = [
        "What was total revenue last month?",
        "Show me top 5 products by revenue",
        "Which traffic source has the highest conversion?",
        "Compare enterprise vs SMB retention",
        "What's our churn rate trend?",
        "Forecast Q3 revenue",
    ]

    render_suggestions(suggestions)

    # Let user type or run a query
    query = st.text_input("Your question", value=st.session_state.get("nlq_query", ""), placeholder="e.g. Show revenue by product last quarter")

    c1, c2 = st.columns([1, 5])
    with c1:
        run_clicked = st.button("Run Query", type="primary", use_container_width=True)
    with c2:
        if st.button("Clear Query", use_container_width=True):
            st.session_state["nlq_query"] = ""
            st.rerun()

    if query or run_clicked:
        render_query_results(query, suggestions)

    section_header("Query history", "A quick view of recent questions")
    st.dataframe(
        {"Query": suggestions[:4], "Result": ["$2.4M", "8 products", "Email 7.8%", "Enterprise 94.2%"], "Time": ["2m ago", "15m ago", "1h ago", "3h ago"]},
        use_container_width=True,
        hide_index=True,
    )

    finish_page()


main()
