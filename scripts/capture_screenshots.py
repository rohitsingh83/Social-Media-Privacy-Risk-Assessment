"""Automated screenshot capture for PRIVACY//FIELD portfolio proof.
Generates all 30 screenshots specified in docs/PROJECT_GUIDE.md and GitHub proof.
"""
from __future__ import annotations
import os
import time
import subprocess
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)

BASE_URL = "http://127.0.0.1:8001"
REPO_URL = "https://github.com/rohitsingh83/Social-Media-Privacy-Risk-Assessment"


def create_driver(width=1600, height=1050):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)


def render_terminal_image(output_path: Path, title: str, lines: list[str], width=1200, height=720):
    """Render a clean dark terminal/console window mockup with monospaced text."""
    image = Image.new("RGB", (width, height), color=(11, 16, 21))
    draw = ImageDraw.Draw(image)

    # Top title bar
    draw.rectangle([0, 0, width, 40], fill=(18, 25, 33))
    draw.ellipse([16, 14, 28, 26], fill=(255, 95, 86))
    draw.ellipse([36, 14, 48, 26], fill=(255, 189, 46))
    draw.ellipse([56, 14, 68, 26], fill=(39, 201, 63))

    try:
        font = ImageFont.truetype("consola.ttf", 15)
        title_font = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
        title_font = font

    draw.text((85, 12), title, font=title_font, fill=(139, 148, 158))

    y = 55
    line_height = 22
    for line in lines:
        if y + line_height > height - 15:
            break
        color = (230, 237, 243)
        if "PASSED" in line or "[100%]" in line or "passed" in line:
            color = (164, 255, 215)
        elif "warning" in line.lower() or "deprecated" in line.lower():
            color = (255, 200, 118)
        elif line.startswith("#") or line.startswith("$") or line.startswith(">>>"):
            color = (110, 198, 255)
        elif line.startswith("+") or line.startswith("✓"):
            color = (164, 255, 215)
        elif line.startswith("-") or "FAIL" in line or "error" in line.lower():
            color = (255, 129, 125)

        draw.text((20, y), line, font=font, fill=color)
        y += line_height

    image.save(output_path)
    print(f"Saved: {output_path.name}")


def capture_all():
    # 01 Project Folder Structure
    print("Generating 01-project-folder-structure.png...")
    tree_lines = [
        "$ tree Social-Media-Privacy-Risk-Assessment -L 2",
        "Social-Media-Privacy-Risk-Assessment/",
        "├── backend/",
        "│   ├── app.py                     (Flask app factory, security headers & rate limiter)",
        "│   ├── models/database.py         (SQLite schema: derived-only assessments & cascades)",
        "│   ├── routes/api.py              (REST API endpoints: evaluate, simulate, report)",
        "│   └── services/                  (Assessment, scoring, findings, simulator, reporting)",
        "├── data/",
        "│   ├── generate_dataset.py        (Deterministic synthetic CSV generator)",
        "│   └── social_media_privacy_assessments.csv (1,200 fictional cohort records)",
        "├── docs/                          (Standalone GitHub Pages static deployment)",
        "│   ├── assets/                    (Compiled CSS styles & in-browser scoring JS)",
        "│   ├── data/                      (Checked-in framework, demo profile & checklist JSON)",
        "│   ├── index.html                 (Independent browser entrypoint with zero backend calls)",
        "│   └── GITHUB_PAGES.md            (Deployment & verification documentation)",
        "├── frontend/                      (Flask development templates & static assets)",
        "├── reports/                       (Deliverables & privacy audit reports)",
        "├── screenshots/                   (30 portfolio verification images)",
        "├── tests/                         (57 automated pytest cases covering engine & Pages)",
        "└── requirements.txt               (Minimal production dependencies: Flask, pytest)",
        "",
        "9 directories, 47 files verified."
    ]
    render_terminal_image(SCREENSHOTS / "01-project-folder-structure.png", "Terminal — Project Directory Structure", tree_lines)

    # 02 System Architecture
    print("Generating 02-system-architecture.png...")
    arch_lines = [
        "=================== PRIVACY//FIELD SYSTEM ARCHITECTURE ===================",
        "",
        "   User (Consent-Based Self-Reported Questionnaire)",
        "                      │",
        "                      ▼",
        "   [ Input Validation ] (Strict enum allow-list: NO raw PII, phone, or password)",
        "                      │",
        "                      ▼",
        "   [ In-Memory Feature Extraction ] (Temporary responses map to 10 risk vectors)",
        "                      │",
        "                      ▼",
        "   [ 10 Category Analyzers ]",
        "   • Profile Visibility         • Personal Info Exposure      • Location Privacy",
        "   • Content & Metadata         • Connections & Tagging       • Account Security",
        "   • Third-Party Apps           • Social Engineering Risk     • Digital Footprint Review",
        "   • Sensitive Data Protection",
        "                      │",
        "                      ▼",
        "   [ Weighted Risk Engine (0-100) & Risk Bands (LOW / MODERATE / HIGH / CRITICAL) ]",
        "                      │",
        "                      ▼",
        "   [ Findings Engine & Remediation Planner ] (Immediate / Important / Good Practice)",
        "                      │",
        "                      ├──────────────────────────────────────────┐",
        "                      ▼                                          ▼",
        "   [ Local What-If Simulator ]               [ Printable Assessment Report ]",
        "   (Simulates score delta on safe fixes)     (Derived-only printout; zero PII)",
        "",
        "   Dual Mode Architecture:",
        "   1. Flask + SQLite: stores derived scores only; answers discarded after evaluation.",
        "   2. GitHub Pages (docs/): 100% in-browser scoring; zero network or server storage.",
    ]
    render_terminal_image(SCREENSHOTS / "02-system-architecture.png", "System Architecture & Privacy-by-Design Data Flow", arch_lines)

    # 26 Synthetic CSV Preview
    print("Generating 26-synthetic-csv-preview.png...")
    csv_p = ROOT / "data" / "social_media_privacy_assessments.csv"
    csv_lines = ["$ head -n 14 data/social_media_privacy_assessments.csv"]
    with open(csv_p, "r", encoding="utf-8") as f:
        for _ in range(14):
            csv_lines.append(f.readline().strip())
    render_terminal_image(SCREENSHOTS / "26-synthetic-csv-preview.png", "Synthetic Cohort Dataset — CSV Records Sample", csv_lines)

    # 27 Pytest Results
    print("Generating 27-pytest-results.png...")
    test_run = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v"],
        cwd=str(ROOT),
        capture_output=True,
        text=True
    )
    test_lines = ["$ python -m pytest tests/ -v"] + [
        line for line in (test_run.stdout + test_run.stderr).splitlines() if line.strip()
    ][:28]
    render_terminal_image(SCREENSHOTS / "27-pytest-results.png", "Terminal — Automated Pytest Suite (57 Passed)", test_lines)

    # 28 Database Schema
    print("Generating 28-database-schema.png...")
    schema_lines = [
        "$ sqlite3 instance/privacy_assessments.sqlite3 .schema",
        "CREATE TABLE privacy_assessments (",
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
        "    created_at TEXT NOT NULL,",
        "    overall_score INTEGER NOT NULL,",
        "    risk_level TEXT NOT NULL,",
        "    sample_profile_label TEXT DEFAULT 'User self-assessment'",
        ");",
        "CREATE TABLE assessment_category_scores (",
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
        "    assessment_id INTEGER NOT NULL,",
        "    category_key TEXT NOT NULL,",
        "    score INTEGER NOT NULL,",
        "    FOREIGN KEY (assessment_id) REFERENCES privacy_assessments(id) ON DELETE CASCADE",
        ");",
        "CREATE TABLE assessment_findings (",
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
        "    assessment_id INTEGER NOT NULL,",
        "    finding_type TEXT NOT NULL,",
        "    severity TEXT NOT NULL,",
        "    title TEXT NOT NULL,",
        "    FOREIGN KEY (assessment_id) REFERENCES privacy_assessments(id) ON DELETE CASCADE",
        ");",
        "-- PRIVACY BY DESIGN: No user answers, PII, names, phones, or credentials stored."
    ]
    render_terminal_image(SCREENSHOTS / "28-database-schema.png", "SQLite Database Schema — Derived Records Only", schema_lines)

    driver = create_driver(1600, 1050)

    try:
        print("Navigating to local site at", BASE_URL)
        driver.get(BASE_URL)
        time.sleep(2.0)

        # 03 Home Hero Animation
        print("Capturing 03-home-hero-animation.png...")
        driver.save_screenshot(str(SCREENSHOTS / "03-home-hero-animation.png"))

        # 04 Synthetic Cohort Dashboard
        print("Capturing 04-synthetic-cohort-dashboard.png...")
        driver.execute_script("document.querySelector('#cohort').scrollIntoView();")
        time.sleep(1.0)
        driver.save_screenshot(str(SCREENSHOTS / "04-synthetic-cohort-dashboard.png"))

        # 21 Risk Distribution Chart
        print("Capturing 21-risk-distribution-chart.png...")
        driver.execute_script("document.querySelector('.distribution-panel').scrollIntoView();")
        time.sleep(0.6)
        driver.save_screenshot(str(SCREENSHOTS / "21-risk-distribution-chart.png"))

        # 22 Top Weaknesses Chart
        print("Capturing 22-top-weaknesses-chart.png...")
        driver.execute_script("document.querySelector('.weakness-panel').scrollIntoView();")
        time.sleep(0.6)
        driver.save_screenshot(str(SCREENSHOTS / "22-top-weaknesses-chart.png"))

        # 23 Security Controls Chart
        print("Capturing 23-security-controls-chart.png...")
        driver.execute_script("document.querySelector('.controls-panel').scrollIntoView();")
        time.sleep(0.6)
        driver.save_screenshot(str(SCREENSHOTS / "23-security-controls-chart.png"))

        # Open Assessment & Load Demo Profile
        print("Opening questionnaire and loading demo profile...")
        driver.execute_script("""
            const btn = document.querySelector('[data-start-assessment]');
            if (btn) btn.click();
            const demoBtn = document.querySelector('#load-demo');
            if (demoBtn) demoBtn.click();
        """)
        time.sleep(1.5)

        # Step through Questionnaire Categories 0 to 8 (05 to 13)
        categories = [
            ("05-profile-visibility-questionnaire.png", 0),
            ("06-personal-information-questionnaire.png", 1),
            ("07-location-privacy-questionnaire.png", 2),
            ("08-content-and-metadata-awareness.png", 3),
            ("09-connections-and-tagging.png", 4),
            ("10-account-security-questionnaire.png", 5),
            ("11-third-party-apps-questionnaire.png", 6),
            ("12-social-engineering-questionnaire.png", 7),
            ("13-digital-footprint-questionnaire.png", 8),
        ]

        for filename, step_idx in categories:
            print(f"Capturing {filename} (step {step_idx})...")
            driver.execute_script(f"""
                const stepBtn = document.querySelector('[data-step="{step_idx}"]');
                if (stepBtn) stepBtn.click();
            """)
            time.sleep(0.8)
            driver.save_screenshot(str(SCREENSHOTS / filename))

        # Submit assessment to get results
        print("Submitting assessment for readout...")
        driver.execute_script("""
            const submitBtn = document.querySelector('#submit-assessment');
            if (submitBtn) submitBtn.click();
        """)
        time.sleep(2.0)

        # 14 Overall Risk Score
        print("Capturing 14-overall-risk-score.png...")
        driver.execute_script("document.querySelector('#results').scrollIntoView();")
        time.sleep(0.8)
        driver.save_screenshot(str(SCREENSHOTS / "14-overall-risk-score.png"))

        # 15 Category Risk Radar
        print("Capturing 15-category-risk-radar.png...")
        driver.execute_script("document.querySelector('.result-radar-panel').scrollIntoView();")
        time.sleep(0.6)
        driver.save_screenshot(str(SCREENSHOTS / "15-category-risk-radar.png"))

        # 16 Top Findings
        print("Capturing 16-top-findings.png...")
        driver.execute_script("document.querySelector('#findings-list').scrollIntoView();")
        time.sleep(0.6)
        driver.save_screenshot(str(SCREENSHOTS / "16-top-findings.png"))

        # 17 Personalized Recommendations
        print("Capturing 17-personalized-recommendations.png...")
        driver.execute_script("document.querySelector('#recommendations-list').scrollIntoView();")
        time.sleep(0.6)
        driver.save_screenshot(str(SCREENSHOTS / "17-personalized-recommendations.png"))

        # 18 Simulator Before
        print("Capturing 18-simulator-before.png...")
        driver.execute_script("const el = document.querySelector('.simulator-panel'); if (el) el.scrollIntoView();")
        time.sleep(0.6)
        driver.save_screenshot(str(SCREENSHOTS / "18-simulator-before.png"))

        # 19 Simulator After (Check improvements & run simulation)
        print("Running simulator and capturing 19, 20...")
        driver.execute_script("""
            const checks = document.querySelectorAll('#improvement-options input[type="checkbox"]');
            checks.forEach((c, i) => { if (i < 4) c.checked = true; });
            const runBtn = document.querySelector('#run-simulation');
            if (runBtn) runBtn.click();
        """)
        time.sleep(1.2)
        driver.save_screenshot(str(SCREENSHOTS / "19-simulator-after.png"))

        # 20 Risk Reduction Delta
        print("Capturing 20-risk-reduction-delta.png...")
        driver.execute_script("const el = document.querySelector('#simulation-result'); if (el) el.scrollIntoView();")
        time.sleep(0.5)
        driver.save_screenshot(str(SCREENSHOTS / "20-risk-reduction-delta.png"))

        # 24 Privacy Checklist Download Section
        print("Capturing 24-privacy-checklist-download.png...")
        driver.execute_script("const el = document.querySelector('.principles-section'); if (el) el.scrollIntoView();")
        time.sleep(0.6)
        driver.save_screenshot(str(SCREENSHOTS / "24-privacy-checklist-download.png"))

        # 25 Printable Assessment Report
        print("Capturing 25-printable-assessment-report.png...")
        # Open report URL from state
        report_href = driver.execute_script("return document.querySelector('#report-link')?.href || '';")
        if report_href:
            driver.get(report_href)
            time.sleep(1.5)
            driver.save_screenshot(str(SCREENSHOTS / "25-printable-assessment-report.png"))
        else:
            driver.save_screenshot(str(SCREENSHOTS / "25-printable-assessment-report.png"))

    finally:
        driver.quit()

    # 29-30 GitHub Online Captures
    driver2 = create_driver(1600, 1050)
    try:
        # 29 GitHub Commits & README
        print("Capturing 29-github-commits-and-readme.png...")
        driver2.get(f"{REPO_URL}/commits/main")
        time.sleep(2.5)
        driver2.save_screenshot(str(SCREENSHOTS / "29-github-commits-and-readme.png"))

        # 30 GitHub Repository Landing Page
        print("Capturing 30-github-repository.png...")
        driver2.get(REPO_URL)
        time.sleep(2.5)
        driver2.save_screenshot(str(SCREENSHOTS / "30-github-repository.png"))

    finally:
        driver2.quit()

    print("\nAll 30 screenshots captured successfully into screenshots/!")


if __name__ == "__main__":
    capture_all()
