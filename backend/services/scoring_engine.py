"""Explainable feature extraction, category scoring, and risk classification."""
from __future__ import annotations

from math import floor
from typing import Mapping

from .questionnaire import CATEGORIES, QUESTION_MAP

DEFAULT_WEIGHTS = {category["key"]: category["weight"] for category in CATEGORIES}
RISK_LEVELS = [
    (20, "LOW"),
    (40, "MODERATE"),
    (70, "HIGH"),
    (100, "CRITICAL"),
]


def _round_half_up(value: float) -> int:
    """Use the same non-negative half-up rounding as JavaScript Math.round."""
    return int(floor(value + 0.5))


def validate_responses(responses: object) -> dict[str, str]:
    """Validate an enum-only payload; reject missing and unknown fields.

    No free text is accepted. In particular, fields such as email, phone,
    password, address, location, or message cannot pass this allow-list.
    """
    if not isinstance(responses, dict):
        raise ValueError("responses must be an object of questionnaire choices")
    expected = set(QUESTION_MAP)
    received = set(responses)
    missing = expected - received
    unknown = received - expected
    if missing:
        raise ValueError(f"Please answer every question; {len(missing)} answer(s) are missing")
    if unknown:
        raise ValueError("Unexpected fields are not accepted")

    cleaned: dict[str, str] = {}
    for qid, value in responses.items():
        if not isinstance(value, str):
            raise ValueError(f"Invalid answer for {qid}")
        value = value.strip().upper()
        if value not in QUESTION_MAP[qid]["risk_by_value"]:
            raise ValueError(f"Invalid answer for {qid}")
        cleaned[qid] = value
    return cleaned


def extract_privacy_features(responses: object) -> dict:
    """Convert safe questionnaire choices into a structured feature dictionary.

    Output is for in-memory scoring. The web API does not persist or echo the
    answer-level feature list.
    """
    clean = validate_responses(responses)
    totals = {
        category["key"]: {"risk_points": 0, "max_points": 0, "feature_count": 0}
        for category in CATEGORIES
    }
    items = {}
    for qid, answer in clean.items():
        question = QUESTION_MAP[qid]
        risk_points = question["risk_by_value"][answer]
        category = question["category"]
        totals[category]["risk_points"] += risk_points
        totals[category]["max_points"] += question["max_points"]
        totals[category]["feature_count"] += 1
        items[qid] = {
            "category": category,
            "risk_points": risk_points,
            "max_points": question["max_points"],
            "risk_ratio": round(risk_points / question["max_points"], 2),
        }
    return {"features": items, "category_totals": totals}


def calculate_category_scores(feature_data: dict) -> dict[str, int]:
    """Blend the category's most severe feature (60%) with its average (40%).

    Peak-weighting ensures that one severe exposure (for example, public
    real-time location) is not hidden by several safe answers in the same
    category. The averaging term still rewards broad, sustained improvements.
    This is an educational rubric choice and should be calibrated before any
    professional use.
    """
    features = feature_data["features"]
    scores: dict[str, int] = {}
    for category in CATEGORIES:
        ratios = [item["risk_ratio"] for item in features.values()
                  if item["category"] == category["key"]]
        if not ratios:
            raw = 0
        else:
            average_risk = sum(ratios) / len(ratios)
            peak_risk = max(ratios)
            raw = (0.60 * peak_risk + 0.40 * average_risk) * 100
        scores[category["key"]] = max(0, min(100, _round_half_up(raw)))
    return scores


def calculate_privacy_risk(category_scores: Mapping[str, int | float],
                           weights: Mapping[str, int | float] | None = None) -> int:
    """Return a weighted 0–100 risk score; higher means higher assessed risk.

    Weight values are percentages or relative values. The calculation
    normalizes by their sum, so any non-negative configuration is supported.
    """
    chosen_weights = dict(DEFAULT_WEIGHTS)
    if weights is not None:
        unknown_weights = set(weights) - set(DEFAULT_WEIGHTS)
        if unknown_weights:
            raise ValueError("Unknown category weight")
        chosen_weights.update(weights)
    if set(category_scores) != set(DEFAULT_WEIGHTS):
        raise ValueError("A score is required for every risk category")
    for key, score in category_scores.items():
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 100:
            raise ValueError(f"Category score for {key} must be between 0 and 100")
    for value in chosen_weights.values():
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise ValueError("Weights must be non-negative numbers")
    total_weight = sum(chosen_weights.values())
    if total_weight <= 0:
        raise ValueError("At least one category weight must be greater than zero")
    weighted_score = sum(category_scores[key] * chosen_weights[key] for key in DEFAULT_WEIGHTS) / total_weight
    return max(0, min(100, _round_half_up(weighted_score)))


def classify_risk(score: int | float) -> str:
    """Apply the educational thresholds defined in the project brief."""
    if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 100:
        raise ValueError("Risk score must be between 0 and 100")
    if score <= 20:
        return "LOW"
    if score <= 40:
        return "MODERATE"
    if score <= 70:
        return "HIGH"
    return "CRITICAL"
