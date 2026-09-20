"""Registry for custom transformation functions."""
from __future__ import annotations

from typing import Callable, Dict


class CustomFunctionRegistry:
    def __init__(self):
        self._fns: Dict[str, Callable] = {}

    def register(self, name: str, fn: Callable):
        self._fns[name] = fn

    def get(self, name: str):
        return self._fns.get(name)

    def all(self):
        return dict(self._fns)


registry = CustomFunctionRegistry()
