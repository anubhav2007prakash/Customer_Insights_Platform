# Churn Prediction Engine

## Overview
The churn prediction engine provides a reusable, production-oriented framework for training churn models, scoring customers, explaining predictions, suggesting retention actions, and monitoring model health.

## Modules
- datasets: prepares customer feature sets for modeling
- preprocessing: generates configurable churn labels
- feature_selection: supports importance-based feature filtering
- training: trains a default Random Forest-style classifier via the shared ML platform trainer
- evaluation: computes model quality metrics
- inference: produces churn probability, risk level, confidence, and metadata
- explainability: generates human-readable explanations and feature drivers
- recommendations: creates actionable retention recommendations
- monitoring: records monitoring metrics over time
- retraining: schedules manual or event-driven retraining
- services: exposes reusable dashboard services

## Lifecycle
1. Prepare a customer dataset from the feature store.
2. Generate churn labels using business rules.
3. Select relevant features.
4. Train a model and evaluate it.
5. Score customers and create explanations.
6. Trigger retention workflows and monitor performance.
7. Schedule retraining based on performance or data drift.
