"""Automated tests for scoring, privacy boundaries, persistence, and API routes."""
from __future__ import annotations

import sqlite3

import pytest

from backend.app import create_app
from backend import app as flask_module
from backend.models.database import get_assessment, initialize_database, save_assessment
from backend.services.assessment_engine import analyze_responses
from backend.services.findings_engine import generate_privacy_findings
from backend.services.improvement_simulator import simulate_improvements
from backend.services.questionnaire import CATEGORIES, QUESTIONS, safe_demo_responses
from backend.services.recommendation_engine import generate_recommendations
from backend.services.reporting import build_report_html, checklist_payload
from backend.services.scoring_engine import (
    calculate_privacy_risk,
    classify_risk,
    extract_privacy_features,
)


def safe_responses():
    result = {}
    for question in QUESTIONS:
        result[question["id"]] = min(
            question["risk_by_value"],
            key=lambda value: (question["risk_by_value"][value], value),
        )
    return result


@pytest.fixture
def app(tmp_path):
    return create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test-privacy.sqlite3"),
        "MAX_CONTENT_LENGTH": 64 * 1024,
    })


@pytest.fixture
def client(app):
    return app.test_client()


# 1. Fully private profile

def test_fully_private_profile_scores_low():
    result = analyze_responses(safe_responses())
    assert result["overall_score"] == 0
    assert result["risk_level"] == "LOW"
    assert result["findings"] == []


# 2. Fictional public demo profile

def test_fictional_demo_profile_is_high_and_explainable():
    result = analyze_responses(safe_demo_responses())
    assert result["overall_score"] == 57
    assert result["risk_level"] == "HIGH"
    assert result["finding_count"] >= 10


# 3–7. Exposure category controls
@pytest.mark.parametrize("qid", ["phone_public", "email_public", "birthday_public", "workplace_public", "education_public"])
def test_public_personal_information_increases_score(qid):
    responses = safe_responses()
    before = analyze_responses(responses)["category_scores"]["personal_info"]["score"]
    responses[qid] = "YES"
    after = analyze_responses(responses)["category_scores"]["personal_info"]["score"]
    assert after > before


# 8–10. Location exposures
@pytest.mark.parametrize("qid", ["current_location_public", "checkins_enabled", "travel_plans_public"])
def test_location_exposure_increases_location_score(qid):
    responses = safe_responses()
    responses[qid] = "YES"
    result = analyze_responses(responses)
    assert result["category_scores"]["location"]["score"] >= 60


# 11. Public posts

def test_public_posts_increase_content_score():
    responses = safe_responses()
    responses["posts_public"] = "YES"
    assert analyze_responses(responses)["category_scores"]["content"]["score"] > 0


# 12. Unknown connections

def test_often_accepting_unknown_connections_is_flagged():
    responses = safe_responses()
    responses["accept_unknown_connections"] = "OFTEN"
    finding_ids = {item["finding_type"] for item in generate_privacy_findings(responses)}
    assert "accept_unknown_connections" in finding_ids


# 13. Tag review

def test_tag_review_disabled_increases_tagging_score():
    responses = safe_responses()
    responses["tag_review_enabled"] = "NO"
    assert analyze_responses(responses)["category_scores"]["tagging"]["score"] > 0


# 14. MFA

def test_mfa_disabled_generates_immediate_recommendation():
    responses = safe_responses()
    responses["mfa_enabled"] = "NO"
    recommendations = generate_recommendations(responses)
    assert any(item["finding_type"] == "mfa_enabled" and item["priority"] == "IMMEDIATE" for item in recommendations)


# 15. Login alerts

def test_login_alerts_disabled_is_detected():
    responses = safe_responses()
    responses["login_alerts_enabled"] = "NO"
    assert any(item["finding_type"] == "login_alerts_enabled" for item in generate_privacy_findings(responses))


# 16. Password reuse awareness

def test_password_reuse_is_detected_without_accepting_password():
    responses = safe_responses()
    responses["password_reuse_reported"] = "YES"
    assert any(item["finding_type"] == "password_reuse_reported" for item in generate_privacy_findings(responses))


# 17. Connected apps

def test_unreviewed_third_party_apps_are_detected():
    responses = safe_responses()
    responses["third_party_apps_reviewed"] = "NO"
    assert analyze_responses(responses)["category_scores"]["third_party"]["score"] > 0


# 18. Suspicious links

def test_frequent_unexpected_link_clicking_is_detected():
    responses = safe_responses()
    responses["clicks_unexpected_links"] = "OFTEN"
    assert any(item["finding_type"] == "clicks_unexpected_links" for item in generate_privacy_findings(responses))


# 19. Historical posts

def test_old_posts_not_reviewed_are_detected():
    responses = safe_responses()
    responses["old_posts_reviewed"] = "NO"
    assert any(item["finding_type"] == "old_posts_reviewed" for item in generate_privacy_findings(responses))


# 20. Privacy settings review

def test_privacy_settings_not_reviewed_are_detected():
    responses = safe_responses()
    responses["privacy_settings_reviewed"] = "NO"
    assert any(item["finding_type"] == "privacy_settings_reviewed" for item in generate_privacy_findings(responses))


# 21. Feature extraction

def test_feature_extraction_returns_structured_category_totals():
    features = extract_privacy_features(safe_responses())
    assert len(features["features"]) == len(QUESTIONS)
    assert set(features["category_totals"]) == {item["key"] for item in CATEGORIES}


# 22. Weighted overall score calculation

def test_overall_score_uses_configured_default_weights():
    scores = {item["key"]: 0 for item in CATEGORIES}
    scores["profile"] = 100
    assert calculate_privacy_risk(scores) == 10


# 23–26. Exact level boundaries
@pytest.mark.parametrize("score, expected", [(20, "LOW"), (40, "MODERATE"), (70, "HIGH"), (71, "CRITICAL")])
def test_risk_level_boundaries(score, expected):
    assert classify_risk(score) == expected


# 27. Personalized recommendations

def test_recommendations_are_personalized_to_findings():
    responses = safe_responses()
    responses["phone_public"] = "YES"
    actions = generate_recommendations(responses)
    assert any("number" in action["recommendation"].lower() for action in actions)


# 28. Improvement simulation

def test_improvement_simulation_reduces_demo_score():
    demo = safe_demo_responses()
    result = simulate_improvements(demo, [
        "phone_public", "birthday_public", "current_location_public", "travel_plans_public",
        "tag_review_enabled", "mfa_enabled", "login_alerts_enabled", "third_party_apps_reviewed",
        "accept_unknown_connections", "old_posts_reviewed", "profile_visibility",
    ])
    assert result["simulated_score"] < result["current_score"]
    assert result["risk_reduction"] > 0
    assert "simulation" in result["disclaimer"].lower()


# 29. Database save and retrieval

def test_database_saves_derived_assessment(tmp_path):
    db_path = tmp_path / "privacy.sqlite3"
    result = analyze_responses(safe_demo_responses())
    initialize_database(db_path)
    save_assessment(db_path, "a" * 32, result)
    retrieved = get_assessment(db_path, "a" * 32)
    assert retrieved["overall_score"] == result["overall_score"]
    assert len(retrieved["category_scores"]) == 10


# 30. Sensitive responses not persisted

def test_database_schema_has_no_raw_response_or_pii_columns(tmp_path):
    db_path = tmp_path / "privacy.sqlite3"
    initialize_database(db_path)
    with sqlite3.connect(db_path) as db:
        names = {row[1].lower() for row in db.execute("PRAGMA table_info(assessments)")}
    assert names == {"assessment_id", "overall_score", "risk_level", "created_at"}
    assert not names.intersection({"responses", "phone", "email", "password", "address", "location", "messages"})


# 31. HTML report

def test_report_contains_scores_recommendations_and_checklist():
    result = analyze_responses(safe_demo_responses())
    result["assessment_id"] = "b" * 32
    html = build_report_html(result)
    assert "Social media privacy report" in html
    assert "Category risk scores" in html
    assert "Privacy checklist" in html
    assert "Print / Save as PDF" in html


# 32. HTML escaping

def test_report_escapes_untrusted_report_fields():
    html = build_report_html({
        "assessment_id": "<script>alert(1)</script>", "overall_score": 0, "risk_level": "LOW",
        "category_scores": {}, "findings": [], "recommendations": [],
    })
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


# 33. Input validation — missing answer

def test_validation_rejects_missing_answers():
    responses = safe_responses()
    responses.pop("phone_public")
    with pytest.raises(ValueError):
        analyze_responses(responses)


# 34. Input validation — unexpected field

def test_validation_rejects_sensitive_extra_fields():
    responses = safe_responses()
    responses["phone_number"] = "+1 415 555 1212"
    with pytest.raises(ValueError):
        analyze_responses(responses)


# 35. Input validation — enum value

def test_validation_rejects_arbitrary_text_answers():
    responses = safe_responses()
    responses["phone_public"] = "Yes, my number is 555-0100"
    with pytest.raises(ValueError):
        analyze_responses(responses)


# 36. Simulation allow-list

def test_simulation_rejects_unapproved_changes():
    with pytest.raises(ValueError):
        simulate_improvements(safe_responses(), ["phone_public", "delete_everything"])


# 37. Checklist length

def test_privacy_checklist_has_at_least_18_items():
    assert len(checklist_payload()) >= 18


# 38. API accepts and returns a derived-only assessment

def test_api_assessment_create_and_read(client):
    response = client.post("/api/assessment", json={"responses": safe_demo_responses()})
    assert response.status_code == 201
    body = response.get_json()
    assert body["risk_level"] == "HIGH"
    assert "responses" not in body
    saved = client.get(f"/api/assessment/{body['assessment_id']}").get_json()
    assert saved["overall_score"] == body["overall_score"]
    assert "responses" not in saved


# 39. API rejects additional identifiers

def test_api_rejects_contact_fields(client):
    responses = safe_responses()
    responses["email"] = "student@example.com"
    response = client.post("/api/assessment", json={"responses": responses})
    assert response.status_code == 400


# 40. API simulation

def test_api_simulation_returns_reduction(client):
    response = client.post("/api/assessment/simulate-improvement", json={
        "responses": safe_demo_responses(),
        "changes": ["phone_public", "mfa_enabled", "current_location_public"],
    })
    assert response.status_code == 200
    assert response.get_json()["simulated_score"] < response.get_json()["current_score"]


# 41. API report route

def test_api_report_is_html_and_contains_no_response_payload(client):
    create = client.post("/api/assessment", json={"responses": safe_demo_responses()}).get_json()
    response = client.get(f"/api/assessment/{create['assessment_id']}/report")
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b"Privacy checklist" in response.data
    assert b"responses" not in response.data


# 42. Delete behavior

def test_api_delete_removes_derived_record(client):
    create = client.post("/api/assessment", json={"responses": safe_demo_responses()}).get_json()
    assessment_id = create["assessment_id"]
    assert client.delete(f"/api/assessment/{assessment_id}").status_code == 200
    assert client.get(f"/api/assessment/{assessment_id}").status_code == 404


# 43. Security headers

def test_security_headers_are_present(client):
    response = client.get("/api/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "geolocation=()" in response.headers["Permissions-Policy"]


# 44. Questionnaire coverage

def test_questionnaire_has_at_least_40_questions_and_ten_categories(client):
    data = client.get("/api/questionnaire").get_json()
    assert data["question_count"] >= 40
    assert len(data["groups"]) == 10


# 45. Synthetic dataset contract

def test_demo_profile_is_explicitly_fictional(client):
    data = client.get("/api/demo-profile").get_json()
    assert data["fictional"] is True
    assert len(data["responses"]) == len(QUESTIONS)
    assert "username" not in data["responses"]


# 46. Basic API rate limit

def test_api_rate_limit_returns_429_after_configured_threshold(monkeypatch, tmp_path):
    flask_module._RATE_STATE.clear()
    monkeypatch.setattr(flask_module, "RATE_LIMIT", 2)
    test_client = create_app({"TESTING": True, "DATABASE_PATH": str(tmp_path / "rate.sqlite3")}).test_client()
    assert test_client.get("/api/health").status_code == 200
    assert test_client.get("/api/health").status_code == 200
    assert test_client.get("/api/health").status_code == 429
    flask_module._RATE_STATE.clear()


# 47. No session cookie is created

def test_api_does_not_create_browser_session(client):
    response = client.get("/api/health")
    assert "Set-Cookie" not in response.headers


# 48. Deletion cascades to category and finding rows

def test_database_delete_cascades_dependent_rows(tmp_path):
    from backend.models.database import delete_assessment
    db_path = tmp_path / "cascade.sqlite3"
    result = analyze_responses(safe_demo_responses())
    initialize_database(db_path)
    save_assessment(db_path, "c" * 32, result)
    assert delete_assessment(db_path, "c" * 32) is True
    with sqlite3.connect(db_path) as db:
        assert db.execute("SELECT COUNT(*) FROM category_scores").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM findings").fetchone()[0] == 0


# 49. Environment-based database configuration

def test_database_path_can_be_configured_with_environment(monkeypatch, tmp_path):
    configured = tmp_path / "from-env.sqlite3"
    monkeypatch.setenv("DATABASE_PATH", str(configured))
    configured_app = create_app({"TESTING": True})
    assert configured_app.config["DATABASE_PATH"] == str(configured)
    assert configured.exists()


# 50. Fully exposed fictional settings profile

def test_fully_exposed_synthetic_profile_scores_critical():
    responses = {
        question["id"]: max(question["risk_by_value"], key=question["risk_by_value"].get)
        for question in QUESTIONS
    }
    result = analyze_responses(responses)
    assert result["overall_score"] == 100
    assert result["risk_level"] == "CRITICAL"
    assert all(item["score"] == 100 for item in result["category_scores"].values())
