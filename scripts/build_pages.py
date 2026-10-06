#!/usr/bin/env python3
"""Build the self-contained, backend-free GitHub Pages bundle in docs/.

Run from the repository root with: python scripts/build_pages.py
The Pages site uses same-folder relative assets and client-side scoring only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.services.dashboard_analytics import load_synthetic_dashboard  # noqa: E402
from backend.services.questionnaire import (  # noqa: E402
    CATEGORIES,
    IMPROVEMENT_ACTIONS,
    QUESTIONS,
    SAFE_IMPROVEMENT_VALUES,
    safe_demo_responses,
)
from backend.services.reporting import checklist_payload  # noqa: E402

DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"
DATA = DOCS / "data"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    groups = []
    for category in CATEGORIES:
        group = {**category, "questions": []}
        for question in QUESTIONS:
            if question["category"] == category["key"]:
                group["questions"].append({
                    key: question[key]
                    for key in (
                        "id", "category", "prompt", "help", "options", "risk_by_value",
                        "max_points", "finding_title", "recommendation", "priority",
                    )
                })
        groups.append(group)

    write_json(DATA / "framework.json", {
        "categories": CATEGORIES,
        "groups": groups,
        "question_count": len(QUESTIONS),
        "safe_improvement_values": SAFE_IMPROVEMENT_VALUES,
        "improvements": IMPROVEMENT_ACTIONS,
        "risk_levels": {"LOW": [0, 20], "MODERATE": [21, 40], "HIGH": [41, 70], "CRITICAL": [71, 100]},
        "model": {"peak_ratio_weight": 0.60, "average_ratio_weight": 0.40},
    })
    write_json(DATA / "dashboard.json", load_synthetic_dashboard(ROOT / "data" / "social_media_privacy_assessments.csv"))
    write_json(DATA / "demo-profile.json", {"fictional": True, "responses": safe_demo_responses()})
    write_json(DATA / "checklist.json", {"checklist": checklist_payload()})

    # GitHub Pages serves docs/ as the root, including for /repository-name/ URLs.
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    html = html.replace('href="/assets/styles.css"', 'href="assets/styles.css"')
    html = html.replace('src="/assets/app.js"', 'src="assets/app.js"')
    html = html.replace('href="/api/privacy-checklist"', 'href="#method"')
    html = html.replace("Answers stay in memory; only derived scores are saved.", "Answers stay in this browser tab only.")
    html = html.replace(
        "Answers are processed in memory; persistence stores derived category scores, score band, finding types, and recommendations only.",
        "This GitHub Pages build stores nothing; answers and results stay in the current browser tab.",
    )
    html = html.replace("Delete an assessment from the local demo database at any time.", "Clear the readout, refresh, or close the tab to discard the current answers.")
    html = html.replace("Delete saved result", "Clear this readout")
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    (ASSETS / "styles.css").write_text((ROOT / "frontend" / "assets" / "styles.css").read_text(encoding="utf-8"), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built GitHub Pages site in {DOCS}")
    print(f"Questions: {len(QUESTIONS)} · synthetic cohort: {load_synthetic_dashboard(ROOT / 'data' / 'social_media_privacy_assessments.csv')['sample_size']}")


if __name__ == "__main__":
    build()
