"""Ranking service for produced recommendations."""
from __future__ import annotations

from typing import Any


class RankingService:
    def rank(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(candidates, key=lambda item: item.get("score", 0), reverse=True)
