#!/usr/bin/env python3
"""Generate a reproducible, fictional dataset for dashboard demos and testing.

No names, usernames, contact values, posts, or real profile data are created.
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.services.assessment_engine import analyze_responses  # noqa: E402
from backend.services.questionnaire import CATEGORIES, QUESTIONS, safe_demo_responses  # noqa: E402

OUTPUT = ROOT / "data" / "social_media_privacy_assessments.csv"

FIELDS = [
    "profile_id", "profile_visibility", "phone_public", "email_public", "birthday_public",
    "location_public", "workplace_public", "education_public", "relationship_public",
    "posts_public", "location_tagging", "travel_posts", "unknown_connections",
    "tag_review_enabled", "third_party_apps_reviewed", "mfa_enabled", "login_alerts_enabled",
    "password_reuse_reported", "suspicious_link_awareness", "old_posts_reviewed",
    "privacy_settings_reviewed", "risk_score", "risk_level",
] + [f"category_{item['key']}" for item in CATEGORIES]


def _weighted_answer(question: dict, rng: random.Random) -> str:
    """Bias fictional records toward safer answers while retaining variety."""
    risk_map = question["risk_by_value"]
    values = list(risk_map)
    min_risk = min(risk_map.values())
    max_risk = max(risk_map.values())
    safe = [value for value in values if risk_map[value] == min_risk]
    low = [value for value in values if risk_map[value] <= min_risk + 1]
    medium = [value for value in values if risk_map[value] == 2]
    risky = [value for value in values if risk_map[value] == max_risk]
    pool = rng.choices(
        [safe or values, low or safe or values, medium or low or values, risky or values],
        weights=[48, 24, 18, 10],
        k=1,
    )[0]
    return rng.choice(pool)


def _truthy_exposure(answer: str) -> str:
    return "true" if answer in {"YES", "SOMETIMES", "OFTEN", "PUBLIC"} else "false"


def _truthy_control(answer: str) -> str:
    return "true" if answer == "YES" else "false"


def generate_records(count: int = 1200, seed: int = 20251006) -> list[dict[str, str | int]]:
    if count < 1000:
        raise ValueError("The project dataset must contain at least 1,000 fictional records")
    rng = random.Random(seed)
    records = []
    for index in range(1, count + 1):
        responses = {question["id"]: _weighted_answer(question, rng) for question in QUESTIONS}
        # Reserve one known, deliberately weak fictional record for a repeatable demo.
        if index == 1:
            responses = safe_demo_responses()
        analysis = analyze_responses(responses)
        row: dict[str, str | int] = {
            "profile_id": f"SYN-{index:06d}",
            "profile_visibility": responses["profile_visibility"],
            "phone_public": _truthy_exposure(responses["phone_public"]),
            "email_public": _truthy_exposure(responses["email_public"]),
            "birthday_public": _truthy_exposure(responses["birthday_public"]),
            "location_public": _truthy_exposure(responses["current_location_public"]),
            "workplace_public": _truthy_exposure(responses["workplace_public"]),
            "education_public": _truthy_exposure(responses["education_public"]),
            "relationship_public": _truthy_exposure(responses["relationship_public"]),
            "posts_public": _truthy_exposure(responses["posts_public"]),
            "location_tagging": _truthy_exposure(responses["geotagging_enabled"]),
            "travel_posts": _truthy_exposure(responses["travel_plans_public"]),
            "unknown_connections": responses["accept_unknown_connections"],
            "tag_review_enabled": _truthy_control(responses["tag_review_enabled"]),
            "third_party_apps_reviewed": _truthy_control(responses["third_party_apps_reviewed"]),
            "mfa_enabled": _truthy_control(responses["mfa_enabled"]),
            "login_alerts_enabled": _truthy_control(responses["login_alerts_enabled"]),
            "password_reuse_reported": _truthy_exposure(responses["password_reuse_reported"]),
            "suspicious_link_awareness": {
                "NEVER": "HIGH", "RARELY": "HIGH", "SOMETIMES": "MEDIUM",
                "OFTEN": "LOW", "NOT_SURE": "UNKNOWN",
            }[responses["clicks_unexpected_links"]],
            "old_posts_reviewed": _truthy_control(responses["old_posts_reviewed"]),
            "privacy_settings_reviewed": _truthy_control(responses["privacy_settings_reviewed"]),
            "risk_score": analysis["overall_score"],
            "risk_level": analysis["risk_level"],
        }
        for category in CATEGORIES:
            row[f"category_{category['key']}"] = analysis["category_scores"][category["key"]]["score"]
        records.append(row)
    return records


def write_dataset(path: Path = OUTPUT, count: int = 1200, seed: int = 20251006) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = generate_records(count=count, seed=seed)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create synthetic privacy assessment rows.")
    parser.add_argument("--count", type=int, default=1200, help="Number of fictional records (minimum 1,000).")
    parser.add_argument("--seed", type=int, default=20251006, help="Deterministic random seed.")
    parser.add_argument("--output", type=Path, default=OUTPUT, help="CSV output path.")
    args = parser.parse_args()
    path = write_dataset(args.output, args.count, args.seed)
    print(f"Generated {args.count:,} fictional records: {path}")


if __name__ == "__main__":
    main()
