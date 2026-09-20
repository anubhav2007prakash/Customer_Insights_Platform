# integrations Module

Bounded context for InsightForge AI integrations domain.

## Structure
- `domain/`       — Domain entities and value objects
- `schemas/`      — Pydantic request/response DTOs
- `repositories/` — Data access (extends SQLAlchemyRepository)
- `services/`     — Business logic (extends BaseService)
- `validators/`   — Input validation rules
- `exceptions/`   — Module-specific exceptions
- `helpers/`      — Module utilities
- `tests/`        — Unit tests

## Rules
1. No business logic in repositories
2. No database access in services (use repositories)
3. No database access in Streamlit pages (use services)
4. All requests validated via Pydantic before service layer
