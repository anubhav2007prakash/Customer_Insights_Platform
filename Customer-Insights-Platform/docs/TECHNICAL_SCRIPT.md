# InsightForge AI — Technical Script

## Overview

Enterprise B2B SaaS customer intelligence platform built with Streamlit. Transforms customer data into actionable decisions via AI, ML, and role-based dashboards.

---

## Tech Stack

| Layer | Tech |
|-------|------|
| UI | Streamlit ≥1.32 |
| Backend | Python 3.12+ |
| Database | PostgreSQL 15+, SQLAlchemy, Alembic |
| ML | scikit-learn, joblib |
| Security | bcrypt, passlib, Pydantic |
| Charts | Plotly |
| Payments | Stripe |
| Storage | boto3 (S3) |
| Scheduling | APScheduler |

---

## Architecture

```
Presentation  →  Application  →  Domain  →  Infrastructure
(Streamlit)      (Dashboards,     (Customer360,  (Postgres, Redis,
                  AI, Analytics)   ML, Auth)      Security)
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `authentication/` | Login, registration, RBAC, sessions (200+ tests) |
| `customer360/` | 360° profiles, lifecycle, health scoring |
| `churn_prediction/` | Churn ML: train, evaluate, explain, monitor |
| `clv_prediction/` | Customer lifetime value prediction |
| `customer_segmentation/` | K-Means, DBSCAN, RFM clustering |
| `forecasting/` | Time-series forecasting & scenarios |
| `recommendation_engine/` | Next-best-action, ranking, feedback loops |
| `ml_platform/` | MLOps: registry, experiments, feature store |
| `analytics/` | Funnels, cohorts, RFM, growth metrics |
| `ai/` | Chatbot, NLQ, insights engine |
| `etl/` | Extract, transform, load pipelines |
| `data_quality/` | Validation, drift, profiling, lineage |
| `feature_store/` | Feature catalog, serving, monitoring |
| `ingestion/` | Connectors, parsers, cleaners |
| `integrations/` | CRM, e-commerce, payment providers |
| `billing/` | Stripe & Razorpay subscription billing |

---

## Security

- **Password hashing**: bcrypt (12 rounds, auto salt)
- **Session mgmt**: Token-based, configurable TTL
- **Account lockout**: 5 failures → 30 min lock
- **RBAC**: Role hierarchy with permission checking
- **Audit logging**: Immutable trail for all auth events
- **Status lifecycle**: Pending → Active → Suspended/Locked/Disabled/Deleted

---

## ML Pipeline

```
Data → Preprocessing → Feature Engineering → Training → Evaluation
  → Explainability (SHAP) → Inference → Monitoring → Retraining
```

Models: Churn prediction, CLV, customer segmentation (K-Means/DBSCAN/RFM), time-series forecasting, recommendation engine.

---

## Data Pipeline (ETL)

```
Extract (API/File) → Transform (Clean/Map/Enrich) → Load (Postgres/Cache)
→ Validate (Quality/Drift/Score) → Monitor (Alerts/Metrics)
```

Quality dimensions: Completeness (>95%), Accuracy (<1% error), Timeliness (<1hr), Uniqueness (<0.1% duplicates).

---

## Database

Core tables: `users`, `organizations`, `roles`, `permissions`, `user_sessions`, `audit_logs`, `customers`, `ml_models`, `features`

Migrations managed by Alembic.

---

## Frontend

- **Components**: Charts (Plotly), dashboard widgets, forms, tables, navigation
- **Design system**: CSS variables for colors, typography, spacing, shadows
- **Multipage routing**: `pages/` directory with Streamlit multipage

---

## Testing

```bash
pytest tests/ -v                    # All tests
pytest authentication/tests/ -v    # Auth tests (200+)
pytest tests/ --cov=.              # With coverage
```

---

## Deployment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
streamlit run app.py               # localhost:8501
```

---

## Key Metrics

| Metric | Target |
|--------|--------|
| Concurrent users | 1000+ |
| API response | <200ms |
| Dashboard load | <3s |
| ML inference | <100ms |
| Uptime | 99.9% |

---

**Status**: Production Ready ✅ | **Tests**: 200+ passing | **Last Updated**: August 2026
