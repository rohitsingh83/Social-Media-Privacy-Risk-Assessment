"""Safe, deterministic "what-if" simulation using approved safer choices."""
from __future__ import annotations

from .questionnaire import SAFE_IMPROVEMENT_VALUES
from .scoring_engine import validate_responses
from .assessment_engine import analyze_responses


def simulate_improvements(responses: object, changes: object) -> dict:
    clean = validate_responses(responses)
    if not isinstance(changes, list) or len(changes) > len(SAFE_IMPROVEMENT_VALUES):
        raise ValueError("changes must be a list of approved improvement IDs")
    if any(not isinstance(item, str) for item in changes):
        raise ValueError("Improvement IDs must be strings")
    if len(changes) != len(set(changes)):
        raise ValueError("Duplicate improvement IDs are not allowed")
    unknown = set(changes) - set(SAFE_IMPROVEMENT_VALUES)
    if unknown:
        raise ValueError("One or more improvements are not approved")

    changed = dict(clean)
    for qid in changes:
        changed[qid] = SAFE_IMPROVEMENT_VALUES[qid]

    before = analyze_responses(clean)
    after = analyze_responses(changed)
    return {
        "current_score": before["overall_score"],
        "current_level": before["risk_level"],
        "simulated_score": after["overall_score"],
        "simulated_level": after["risk_level"],
        "risk_reduction": max(0, before["overall_score"] - after["overall_score"]),
        "score_delta": after["overall_score"] - before["overall_score"],
        "changes_applied": changes,
        "category_scores_before": before["category_scores"],
        "category_scores_after": after["category_scores"],
        "disclaimer": "Framework simulation only; this is not a guarantee of real-world safety.",
    }
