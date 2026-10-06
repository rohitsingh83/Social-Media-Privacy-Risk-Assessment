"""Generate transparent findings from elevated questionnaire features."""
from __future__ import annotations

from .questionnaire import CATEGORIES, QUESTION_MAP
from .scoring_engine import extract_privacy_features

PRIORITY_ORDER = {"IMMEDIATE": 0, "IMPORTANT": 1, "GOOD PRACTICE": 2}


def generate_privacy_findings(responses: object) -> list[dict]:
    features = extract_privacy_features(responses)["features"]
    category_labels = {item["key"]: item["label"] for item in CATEGORIES}
    findings = []
    for qid, feature in features.items():
        points = feature["risk_points"]
        if points <= 0:
            continue
        question = QUESTION_MAP[qid]
        severity = "HIGH" if points >= 3 else ("MEDIUM" if points >= 2 else "LOW")
        findings.append({
            "finding_type": qid,
            "category": feature["category"],
            "category_label": category_labels[feature["category"]],
            "title": question["finding_title"],
            "description": question["help"],
            "severity": severity,
            "priority": question["priority"],
            "risk_points": points,
            "recommendation": question["recommendation"],
        })
    findings.sort(key=lambda finding: (
        PRIORITY_ORDER.get(finding["priority"], 9),
        -finding["risk_points"],
        finding["category_label"],
    ))
    return findings
