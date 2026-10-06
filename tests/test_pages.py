"""GitHub Pages bundle checks: relative assets, static data, and no API dependency."""
from __future__ import annotations

import json
import re
from pathlib import Path

from backend.services.questionnaire import SAFE_IMPROVEMENT_VALUES, safe_demo_responses

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_pages_bundle_has_static_entrypoint_assets_and_data():
    expected = [
        DOCS / "index.html", DOCS / ".nojekyll", DOCS / "assets" / "app.js",
        DOCS / "assets" / "styles.css", DOCS / "data" / "framework.json",
        DOCS / "data" / "dashboard.json", DOCS / "data" / "demo-profile.json",
        DOCS / "data" / "checklist.json",
    ]
    assert all(path.is_file() for path in expected)


def test_pages_questionnaire_contains_56_questions_and_ten_categories():
    framework = json.loads((DOCS / "data" / "framework.json").read_text(encoding="utf-8"))
    assert framework["question_count"] == 56
    assert len(framework["groups"]) == 10
    assert sum(len(group["questions"]) for group in framework["groups"]) == 56


def test_pages_demo_profile_matches_safe_python_fixture():
    demo = json.loads((DOCS / "data" / "demo-profile.json").read_text(encoding="utf-8"))
    assert demo["fictional"] is True
    assert demo["responses"] == safe_demo_responses()


def test_pages_simulation_allowlist_matches_server_model():
    framework = json.loads((DOCS / "data" / "framework.json").read_text(encoding="utf-8"))
    assert framework["safe_improvement_values"] == SAFE_IMPROVEMENT_VALUES
    assert all(action["id"] in SAFE_IMPROVEMENT_VALUES for action in framework["improvements"])


def test_pages_assets_use_relative_urls_for_repository_subpaths():
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    assert 'href="assets/styles.css"' in html
    assert 'src="assets/app.js"' in html
    assert not re.search(r"(?:src|href)=\"/", html)


def test_pages_javascript_does_not_call_backend_or_localhost():
    script = (DOCS / "assets" / "app.js").read_text(encoding="utf-8").lower()
    assert "/api/" not in script
    assert "localhost" not in script
    assert "127.0.0.1" not in script
    assert "data/framework.json" in script


def test_pages_dashboard_is_only_synthetic_aggregate_data():
    stats = json.loads((DOCS / "data" / "dashboard.json").read_text(encoding="utf-8"))
    assert stats["sample_size"] == 1200
    assert "Synthetic" in stats["source"]
    assert "recent" not in stats
    assert "username" not in stats
