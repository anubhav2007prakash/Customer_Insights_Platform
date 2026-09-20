from utils.navigation import get_role_nav_sections
from utils.sample_data import get_ai_insights, get_ai_suggestions, get_alerts, get_recent_activities


def test_role_specific_alerts_and_activity_feed() -> None:
    analyst_alerts = get_alerts("Data Analyst")
    analyst_activity = get_recent_activities(4, "Data Analyst")

    assert analyst_alerts[0]["title"].startswith("Data quality")
    assert any("quality" in item["text"].lower() for item in analyst_activity)


def test_role_specific_ai_center_content() -> None:
    scientist_insights = get_ai_insights("Data Scientist")
    scientist_suggestions = get_ai_suggestions("Data Scientist")

    assert scientist_insights[0]["title"].startswith("Model")
    assert any("experiment" in suggestion.lower() for suggestion in scientist_suggestions)


def test_role_specific_navigation_labels() -> None:
    analyst_sections = get_role_nav_sections("Data Analyst")
    labels = [item.label for section in analyst_sections for item in section.items]

    assert any(label == "Dashboard · Analysis" for label in labels)
    assert any(label == "AI Center · Analysis" for label in labels)
