# InsightForge AI

**Transform Customer Data into Intelligent Business Decisions.**

Enterprise-grade B2B SaaS customer intelligence platform built entirely with Streamlit.

## Quick Start

```bash
cd Customer-Insights-Platform
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

## Features

- Executive dashboard with KPIs, charts, AI insights
- Customer 360° directory with filters, cards, and profiles
- Advanced analytics (funnel, Sankey, treemap, heatmap, radar)
- AI Center with chat, NLQ, predictions, and forecasting
- Marketing, sales, reports, data manager, integrations
- Admin, settings, dark/light theme support

## Architecture

```
components/     Reusable UI, charts, layouts, navigation
utils/          Theme engine, sample data, helpers
assets/styles/  Design system CSS
pages/          Streamlit multipage routes
app.py          Landing entry point
```

## Demo Login

Use any credentials on the login page, or go directly to **Open Dashboard** from the landing page.
