"""Turn findings into a concise, prioritized coaching plan."""
from __future__ import annotations

from .findings_engine import generate_privacy_findings


def generate_recommendations(responses: object) -> list[dict]:
    """Return deduplicated advice without copying any submitted answers."""
    findings = generate_privacy_findings(responses)
    seen: set[tuple[str, str]] = set()
    recommendations = []
    for finding in findings:
        key = (finding["finding_type"], finding["recommendation"])
        if key in seen:
            continue
        seen.add(key)
        recommendations.append({
            "finding_type": finding["finding_type"],
            "category": finding["category"],
            "category_label": finding["category_label"],
            "risk": finding["title"],
            "recommendation": finding["recommendation"],
            "priority": finding["priority"],
        })
    return recommendations
