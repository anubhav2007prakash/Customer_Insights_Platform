# CLV Prediction Engine

## Overview
The CLV prediction engine provides reusable regression-based services for predicting customer lifetime value, assigning customer tiers, forecasting revenue, generating explanations, monitoring model performance, and scheduling retraining.

## Modules
- datasets: prepares customer feature sets for modeling
- preprocessing: creates configurable target horizons for CLV prediction
- feature_selection: supports importance-based feature filtering
- training: trains a default random forest regressor through the shared ML platform trainer
- evaluation: records key regression metrics such as MAE, MSE, RMSE, R2, and MAPE
- inference: generates per-customer CLV predictions with confidence and metadata
- forecasting: produces revenue forecasts for horizons and segments
- customer_tiers: assigns business tiers such as Platinum and Gold
- monitoring: tracks metrics over time
- retraining: schedules manual or event-driven retraining
- services: exposes reusable dashboard services
