"""Aggregate statistics from the checked-in synthetic cohort (never real users)."""
from __future__ import annotations

import csv
from pathlib import Path

from .questionnaire import CATEGORIES

WEAKNESS_LABELS = {
    "phone_public": "Phone visibility",
    "email_public": "Email visibility",
    "birthday_public": "Birth-date visibility",
    "location_public": "Location exposure",
    "travel_posts": "Travel timing",
    "unknown_connections": "Unfamiliar connections",
    "tag_review_enabled": "Tag review disabled",
    "mfa_enabled": "MFA disabled",
    "third_party_apps_reviewed": "Connected apps not reviewed",
    "old_posts_reviewed": "Older posts not reviewed",
}


def _is_risky(value: str, key: str) -> bool:
    value = str(value).strip().upper()
    if key in {"unknown_connections"}:
        return value in {"SOMETIMES", "OFTEN"}
    if key in {"tag_review_enabled", "mfa_enabled", "third_party_apps_reviewed", "old_posts_reviewed"}:
        return value in {"FALSE", "0", "NO"}
    return value in {"TRUE", "1", "YES", "SOMETIMES", "PUBLIC"}


def load_synthetic_dashboard(csv_path: str | Path) -> dict:
    path = Path(csv_path)
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return {"sample_size": 0, "average_score": 0, "risk_distribution": {}, "category_averages": [], "top_weaknesses": [], "security_controls": []}

    n = len(rows)
    average = sum(int(row["risk_score"]) for row in rows) / n
    distribution = {level: 0 for level in ("LOW", "MODERATE", "HIGH", "CRITICAL")}
    for row in rows:
        distribution[row["risk_level"]] = distribution.get(row["risk_level"], 0) + 1
    distribution = {key: round(value * 100 / n, 1) for key, value in distribution.items()}

    category_averages = []
    for category in CATEGORIES:
        column = f"category_{category['key']}"
        values = [int(row[column]) for row in rows if column in row]
        category_averages.append({
            "key": category["key"], "label": category["short"],
            "score": round(sum(values) / len(values), 1) if values else 0,
            "weight": category["weight"],
        })

    weakness_rates = []
    for key, label in WEAKNESS_LABELS.items():
        count = sum(_is_risky(row.get(key, ""), key) for row in rows)
        weakness_rates.append({"key": key, "label": label, "rate": round(count * 100 / n, 1)})
    weakness_rates.sort(key=lambda item: (-item["rate"], item["label"]))

    control_fields = [
        ("mfa_enabled", "MFA enabled", True),
        ("login_alerts_enabled", "Login alerts", True),
        ("tag_review_enabled", "Tag review", True),
        ("third_party_apps_reviewed", "Apps reviewed", True),
    ]
    controls = []
    for key, label, _ in control_fields:
        enabled = sum(str(row.get(key, "")).upper() in {"TRUE", "1", "YES"} for row in rows)
        controls.append({"key": key, "label": label, "enabled_percent": round(enabled * 100 / n, 1)})

    return {
        "sample_size": n,
        "source": "Synthetic fictional assessment records only",
        "average_score": round(average, 1),
        "risk_distribution": distribution,
        "category_averages": category_averages,
        "top_weaknesses": weakness_rates[:6],
        "security_controls": controls,
    }
