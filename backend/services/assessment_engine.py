"""One-call orchestration for the privacy assessment pipeline."""
from __future__ import annotations

from datetime import datetime, timezone

from .findings_engine import generate_privacy_findings
from .questionnaire import CATEGORIES, QUESTION_MAP
from .recommendation_engine import generate_recommendations
from .scoring_engine import (
    calculate_category_scores,
    calculate_privacy_risk,
    classify_risk,
    extract_privacy_features,
    validate_responses,
)


def analyze_responses(responses: object) -> dict:
    """Validate answers, extract features, score categories, and coach safely."""
    clean = validate_responses(responses)
    feature_data = extract_privacy_features(clean)
    category_score_values = calculate_category_scores(feature_data)
    categories = {}
    for category in CATEGORIES:
        key = category["key"]
        categories[key] = {
            "label": category["label"],
            "short": category["short"],
            "weight": category["weight"],
            "score": category_score_values[key],
        }

    overall = calculate_privacy_risk(category_score_values)
    findings = generate_privacy_findings(clean)
    recommendations = generate_recommendations(clean)
    high_risk_categories = [
        {"key": key, "label": item["label"], "score": item["score"]}
        for key, item in categories.items() if item["score"] >= 41
    ]
    control_ids = [qid for qid, question in QUESTION_MAP.items()
                   if question["risk_by_value"].get("YES") == 0 and
                   set(question["risk_by_value"]) == {"YES", "NO", "SOMETIMES", "NOT_SURE"}]
    enabled_controls = sum(clean[qid] == "YES" for qid in control_ids)

    return {
        "overall_score": overall,
        "risk_level": classify_risk(overall),
        "category_scores": categories,
        "findings": findings,
        "recommendations": recommendations,
        "finding_count": len(findings),
        "recommendation_count": len(recommendations),
        "high_risk_categories": high_risk_categories,
        "security_controls_enabled": enabled_controls,
        "security_controls_total": len(control_ids),
        "assessed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "disclaimer": (
            "Educational self-assessment only. Scores reflect selected answers and model assumptions; "
            "they are not a prediction or guarantee of compromise or safety."
        ),
    }
