"""Model registry for approved and versioned models."""
from __future__ import annotations

from typing import Any


class ModelRegistry:
    def __init__(self) -> None:
        self._models: dict[str, dict[str, Any]] = {}

    def register(self, model: dict[str, Any]) -> dict[str, Any]:
        model_id = model.get("model_id") or f"model-{len(self._models) + 1}"
        registered = dict(model)
        registered["model_id"] = model_id
        registered.setdefault("status", "draft")
        self._models[model_id] = registered
        return registered

    def get(self, model_id: str) -> dict[str, Any] | None:
        return self._models.get(model_id)

    def approve(self, model_id: str) -> dict[str, Any] | None:
        model = self._models.get(model_id)
        if model is not None:
            model["status"] = "approved"
        return model
