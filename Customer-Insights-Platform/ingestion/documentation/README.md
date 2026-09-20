# Data Ingestion Engine

This module provides the Data Ingestion Engine for InsightForge AI.

See the `ingestion/services/ingestion_service.py` for the primary import workflow (preview, validate, map, clean, import).

Connectors, parsers, validators, mappers, and cleaners follow Clean Architecture to make adding new sources straightforward.
