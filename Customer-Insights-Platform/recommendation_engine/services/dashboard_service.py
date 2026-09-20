"""Dashboard service returning personalized recommendations."""
from __future__ import annotations

from typing import Any

from recommendation_engine.candidate_generation.service import CandidateGenerationService
from recommendation_engine.ranking.service import RankingService
from recommendation_engine.scoring.service import ScoringService


class RecommendationDashboardService:
    def __init__(self) -> None:
        self._candidate_generation = CandidateGenerationService()
        self._ranking = RankingService()
        self._scoring = ScoringService()

    def get_personalized_recommendations(self, customers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = []
        for customer in customers:
            candidates = self._candidate_generation.generate(customer)
            ranked = self._ranking.rank(candidates)
            scored = [self._scoring.score(customer, item) for item in ranked]
            result.append({"customer_id": customer.get("customer_id"), "recommendations": scored})
        return result
