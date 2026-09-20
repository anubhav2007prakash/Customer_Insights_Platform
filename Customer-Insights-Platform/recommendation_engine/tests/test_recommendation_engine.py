import pytest

from recommendation_engine.datasets.service import RecommendationDatasetService
from recommendation_engine.candidate_generation.service import CandidateGenerationService
from recommendation_engine.ranking.service import RankingService
from recommendation_engine.scoring.service import ScoringService
from recommendation_engine.next_best_action.service import NextBestActionService
from recommendation_engine.feedback.service import FeedbackService
from recommendation_engine.monitoring.service import MonitoringService
from recommendation_engine.evaluation.service import EvaluationService
from recommendation_engine.services.dashboard_service import RecommendationDashboardService


@pytest.fixture
def sample_customer() -> dict:
    return {
        "customer_id": "c1",
        "segment": "champion",
        "clv": 6000,
        "churn_probability": 0.1,
        "health_score": 90,
        "loyalty_score": 88,
        "purchase_history": ["p1", "p2"],
        "preferences": ["premium"],
        "products": ["product_a", "product_b"],
    }


def test_candidate_generation(sample_customer: dict) -> None:
    service = CandidateGenerationService()
    candidates = service.generate(sample_customer)
    assert candidates
    assert candidates[0]["product_id"]


def test_ranking_and_scoring(sample_customer: dict) -> None:
    ranking = RankingService()
    scoring = ScoringService()
    ranked = ranking.rank([{"product_id": "p1", "score": 0.7}, {"product_id": "p2", "score": 0.3}])
    scored = scoring.score(sample_customer, ranked[0])
    assert ranked[0]["product_id"] == "p1"
    assert scored["priority"] in {"high", "medium", "low"}


def test_next_best_action(sample_customer: dict) -> None:
    service = NextBestActionService()
    action = service.generate(sample_customer)
    assert action["action_type"]


def test_feedback_and_monitoring(sample_customer: dict) -> None:
    feedback = FeedbackService()
    monitoring = MonitoringService()
    feedback.record_feedback(sample_customer["customer_id"], "accepted")
    monitoring.record_metrics({"acceptance_rate": 0.8})
    assert feedback.get_feedback(sample_customer["customer_id"])[-1]["status"] == "accepted"
    assert monitoring.get_metrics()[-1]["acceptance_rate"] == 0.8


def test_evaluation_and_dashboard(sample_customer: dict) -> None:
    evaluation = EvaluationService()
    dashboard = RecommendationDashboardService()
    dataset = RecommendationDatasetService().prepare_dataset([sample_customer])
    metrics = evaluation.evaluate(dataset, [{"product_id": "p1"}])
    recommendations = dashboard.get_personalized_recommendations([sample_customer])
    assert metrics["precision_at_k"] >= 0.0
    assert recommendations[0]["customer_id"] == sample_customer["customer_id"]
