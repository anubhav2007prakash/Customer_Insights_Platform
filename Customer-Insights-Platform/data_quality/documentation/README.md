# Data Quality and Schema Management

This module provides enterprise-grade data quality capabilities for InsightForge AI with clean architecture and multi-tenant support.

## Components

- `profiling` — automatic dataset profiling and historical storage.
- `schema` — schema detection, validation, and versioning.
- `validation` — rule-based validation, invalid format detection, and schema enforcement.
- `rules` — configurable and extensible validation rules.
- `scoring` — quality scoring across completeness, validity, uniqueness, consistency, accuracy, and timeliness.
- `lineage` — dataset lineage capture for source, transformation, validation, and export metadata.
- `versioning` — dataset and schema version management.
- `drift` — dataset drift detection versus historical baselines.
- `governance` — policy enforcement for retention, sensitive fields, required attributes, and compliance.
- `monitoring` — runtime metric collection for dashboards.

## Architecture

- Clean separation of services, repositories, domain models, and utilities.
- `DataQualityService` orchestrates profile, schema, validation, scoring, drift, lineage, and governance.
- Persistence layers store profiles, scores, schemas, validation results, reports, lineage, and audit logs.

## Usage

Use `DataQualityService.execute_quality_run()` to evaluate a dataset and store the resulting quality metadata.
