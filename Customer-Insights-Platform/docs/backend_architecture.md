# InsightForge AI — Backend Architecture

Production-grade clean architecture foundation for enterprise B2B SaaS.

---

## Layer Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                          │
│         presentation/streamlit/  (pages, components)         │
│         ❌ NO database access allowed                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ get_service() / with_uow()
┌──────────────────────────▼──────────────────────────────────┐
│                  APPLICATION LAYER                           │
│         application/  — Use cases, orchestration             │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   BUSINESS LAYER                             │
│         modules/*/services/  — Business rules ONLY           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    DOMAIN LAYER                              │
│         domain/  — Entities, value objects, aggregates       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  REPOSITORY LAYER                            │
│         modules/*/repositories/  — CRUD, search, pagination  │
│         ❌ NO business logic allowed                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│               INFRASTRUCTURE / PERSISTENCE                   │
│         infrastructure/  +  database/  (SQLAlchemy ORM)      │
└─────────────────────────────────────────────────────────────┘
```

---

## Request Flow (Mandatory)

Every feature MUST follow:

```
Streamlit Page
    ↓  Pydantic validation (schemas/)
Service Layer
    ↓  Business rules, permissions, events
Repository Layer
    ↓  CRUD only
SQLAlchemy ORM (database/models/)
    ↓
PostgreSQL
    ↓
Response DTO → Page render
```

---

## Folder Structure

```
Customer-Insights-Platform/
├── bootstrap.py                 # Application startup
├── core/                        # Shared kernel (framework)
│   ├── config/                  # Settings (dev/test/prod)
│   ├── logging/                 # Centralized logging
│   ├── exceptions/              # Exception hierarchy
│   ├── interfaces/              # Ports (Repository, UoW, EventBus, Cache)
│   ├── di/                      # Dependency injection container
│   ├── events/                  # Domain event system
│   ├── validation/              # Pydantic validation framework
│   ├── security/                # Password, RBAC, sanitization
│   └── types/                   # TenantContext, Pagination, etc.
├── domain/                      # Domain layer base classes
│   └── base/                    # Entity, ValueObject, AggregateRoot
├── application/                 # Use case layer
│   └── base/                    # UseCase base class
├── infrastructure/              # Adapters
│   ├── persistence/             # SQLAlchemyRepository, UnitOfWork
│   ├── cache/                   # InMemoryCache (Redis later)
│   └── tasks/                   # Background task scheduler port
├── modules/                     # Bounded contexts (13 modules)
│   ├── auth/
│   ├── customer/
│   ├── analytics/
│   ├── marketing/
│   ├── sales/
│   ├── reports/
│   ├── ai/
│   ├── ml/
│   ├── forecasting/
│   ├── notifications/
│   ├── integrations/
│   ├── settings/
│   ├── admin/
│   └── base.py                  # BaseService, BaseModuleRepository
├── presentation/                # UI bridge
│   └── streamlit/
│       ├── dependencies.py      # get_service(), with_uow()
│       └── context.py           # TenantContext from session
├── database/                    # Persistence models (ORM)
├── pages/                       # Streamlit pages (presentation)
├── components/                  # Streamlit UI components
└── tests/                       # Unit & integration tests
```

Each module under `modules/` contains:

| Folder | Responsibility |
|--------|----------------|
| `domain/` | Domain entities (not ORM) |
| `schemas/` | Pydantic request/response DTOs |
| `repositories/` | Data access |
| `services/` | Business logic |
| `validators/` | Input validation rules |
| `exceptions/` | Module-specific errors |
| `helpers/` | Module utilities |
| `tests/` | Module unit tests |

---

## SOLID Compliance

| Principle | Implementation |
|-----------|----------------|
| **Single Responsibility** | Services = business rules; Repositories = data access |
| **Open/Closed** | Extend via new modules without modifying core |
| **Liskov Substitution** | All repos implement `Repository` port |
| **Interface Segregation** | `ReadRepository` / `WriteRepository` split |
| **Dependency Inversion** | Services depend on interfaces, not implementations |

---

## Dependency Injection

```python
from core.di.container import get_container
from core.interfaces.event_bus import EventBusPort

container = get_container()
container.register_factory(CustomerService, lambda: CustomerService(...))
service = container.resolve(CustomerService)
```

Streamlit pages use:

```python
from presentation.streamlit.dependencies import get_service, with_uow
from presentation.streamlit.context import get_tenant_context

ctx = get_tenant_context()
service = get_service(CustomerService)
result = service.list_customers(ctx, pagination)
```

---

## Configuration

Environment-aware via Pydantic Settings:

| Variable | Purpose |
|----------|---------|
| `ENVIRONMENT` | development / testing / production |
| `DB_*` | PostgreSQL connection |
| `SECURITY_*` | JWT, bcrypt, session TTL |
| `AI_*` | Model defaults, token limits |
| `LOG_*` | Log level, format (json/text) |
| `CACHE_*` | Cache backend and TTL |

Copy `.env.example` → `.env` — never commit secrets.

---

## Exception Hierarchy

```
InsightForgeError
├── AuthenticationError / AuthorizationError / SessionExpiredError
├── ValidationError / NotFoundError / ConflictError
├── DatabaseError / ConfigurationError / CacheError
├── BusinessRuleError / TenantError
├── AIError / PredictionError / ModelNotFoundError
├── IntegrationError / SyncError / ExportError
└── FileValidationError
```

Presentation layer uses `handle_exception()` for safe user messages.

---

## Event Architecture

Loosely coupled internal events:

| Event | Trigger |
|-------|---------|
| `CustomerCreated` | New customer registered |
| `CampaignCompleted` | Marketing campaign finishes |
| `PredictionGenerated` | ML inference completes |
| `ReportExported` | Report export succeeds |
| `InvoicePaid` | Payment confirmed |
| `AIInsightGenerated` | AI insight created |

```python
from core.events.base import CustomerCreated
from core.interfaces.event_bus import EventBusPort

bus.publish(CustomerCreated(customer_id=id, metadata=...))
```

Replace `InMemoryEventBus` with Redis/RabbitMQ at scale.

---

## Background Tasks (Future)

`TaskSchedulerPort` supports:

- Scheduled reports
- Model retraining
- Forecast updates
- Email notifications
- Data sync jobs
- Analytics cache refresh

---

## Security

- **Passwords**: bcrypt via passlib (`core/security/password.py`)
- **RBAC**: `PermissionChecker` + `@require_permission` decorator
- **Input**: Pydantic validation + HTML escape sanitization
- **Files**: Filename sanitization, path traversal prevention
- **SQL**: SQLAlchemy parameterized queries only
- **Tenancy**: `TenantContext` enforced on every repository query

---

## Testing

```bash
pytest tests/ -v
```

Every service, repository, validator must be independently testable via DI and fixtures in `tests/conftest.py`.

---

## Adding a New Module

1. Create `modules/<name>/` with standard subfolders
2. Define domain entities in `modules/<name>/domain/`
3. Create Pydantic schemas in `schemas/`
4. Implement repository extending `SQLAlchemyRepository`
5. Implement service extending `BaseService`
6. Register in `bootstrap.py` DI container
7. Register event handlers in `EventRegistry`
8. Call from Streamlit via `get_service()` — never query DB in pages
9. Write tests in `modules/<name>/tests/`

---

## Bootstrap

```python
# app.py
from bootstrap import bootstrap
bootstrap()
```

---

*InsightForge AI Backend Architecture v1.0*
