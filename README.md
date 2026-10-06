# Social Media Privacy Risk Assessment Framework

> **PRIVACY//FIELD** is a defensive, consent-based privacy self-assessment dashboard. It never connects to social platforms, scrapes profiles, or asks for the underlying sensitive information.

## Overview

People can unintentionally expose contact details, location context, workplace or school clues, social connections, older posts, and account-security weaknesses. This student project turns privacy hygiene into an explainable coaching workflow: answer a settings-and-habits questionnaire, review category scores, choose practical fixes, simulate the possible score change, and print a minimal report.

**The assessment asks whether a detail is visible—not what the detail is.** It does not ask for phone numbers, email addresses, full birth dates, passwords, home addresses, precise locations, private messages, account handles, photos, or platform credentials.

## Problem Statement

Privacy settings are distributed across platforms and change over time. A person may have a strong password but a public profile, real-time location habits, or unreviewed connected applications. A repeatable, user-controlled checkup can turn those broad concepts into concrete actions without monitoring or profiling real people.

## Objectives

- Assess ten privacy and account-safety categories using 56 self-reported questions.
- Produce an explainable 0–100 score, risk band, findings, and prioritized recommendations.
- Offer a safe “what-if” simulator that changes only the framework's temporary answer copy.
- Demonstrate privacy-by-design, input validation, minimal SQLite persistence, defensive API design, and automated tests.
- Provide an aggregate awareness dashboard backed by 1,200 deterministic fictional records.

## Cybersecurity Relevance

The project demonstrates privacy engineering, risk analysis, defensive application development, security awareness, data analytics, and GRC-style documentation. It is useful as a **personal learning and coaching artifact**, not as an employee-screening or student-surveillance tool.

Potentially related roles include Cybersecurity Analyst, Privacy Analyst, GRC Analyst, SOC Analyst, Security Consultant, IAM Analyst, Security Awareness Specialist, and Privacy Engineer. Relevant skills demonstrated: Python, Flask, SQLite, REST API design, input validation, scoring models, privacy-by-design, synthetic data generation, HTML/CSS/JavaScript, accessible UI patterns, testing, threat modeling, and technical writing.

## Privacy vs Security

- **Privacy** is about how information is collected, exposed, shared, and used.
- **Security** is about protecting accounts, systems, and information from unauthorized access or misuse.

They overlap but are not interchangeable. MFA and a unique password can strengthen account security, while a public phone number or public location posts remain a privacy exposure. **Strong account security ≠ strong privacy.** Conversely, a private profile can still have weak authentication.

## Features

- 56-question guided assessment across ten categories.
- 56-question count is supplied by the API; every answer is a fixed enum, with “Not sure” available.
- Fictional demo profile preset for a repeatable classroom walkthrough.
- Overall and category scores with a custom SVG radar chart and risk bands.
- Explainable findings plus immediate, important, and good-practice recommendations.
- Improvement simulator uses a fixed safe-value allow-list (Python API mode or static JSON in Pages mode).
- Printable HTML report with a built-in “Print / Save as PDF” control; Pages creates it in the browser.
- Downloadable/printable privacy checklist.
- Animated, responsive dashboard with synthetic aggregate data and no external analytics or font dependencies.
- Backend-free GitHub Pages build: questionnaire, scoring, simulator, report, and checklist run entirely in the browser under `docs/`.
- Flask mode stores derived scores and findings only; submitted answers are not saved. GitHub Pages mode stores nothing at all.
- Delete endpoint removes a saved Flask assessment; Pages mode clears the in-memory readout.

## Architecture

```text
User
  ↓
Privacy Questionnaire (56 fixed-choice questions)
  ↓
Input Validation (known keys + known enum values only)
  ↓
Feature Extraction (in memory; never persisted)
  ↓
Ten Category Analyzers → Category Scores (0–100)
  ↓
Weighted Risk Engine → Risk Band
  ↓
Findings + Personalized Recommendations
  ↓
Dashboard / Improvement Simulator / Printable Report

Synthetic CSV (1,200 fictional records) → Aggregate Dashboard

GitHub Pages: browser UI + checked-in JSON → in-browser validation/scoring → local report blob
(no Flask, SQLite, cookies, external services, or saved visitor answers)
```

Vector architecture diagram: [`docs/architecture.svg`](docs/architecture.svg).

## Project Structure

```text
backend/app.py                    Flask app factory and security headers
backend/routes/api.py             REST API blueprint
backend/models/database.py        Derived-only SQLite schema
backend/services/                 Questionnaire, scoring, findings, coaching, simulator, reports
frontend/index.html               Dashboard shell
frontend/assets/                  Animated styling and client-side interactions
data/generate_dataset.py          Reproducible synthetic CSV generator
data/social_media_privacy_assessments.csv  1,200 fictional rows
tests/test_assessment.py          Flask engine/API tests
tests/test_pages.py               GitHub Pages static-bundle tests
docs/index.html                   GitHub Pages entrypoint (published from /docs)
docs/assets/ + docs/data/          Static CSS/JS and generated framework JSON
scripts/build_pages.py             Regenerate the independent static site
docs/*.md                          Student report, guide, deployment, threat model, test matrix
reports/                           Optional generated deliverables
screenshots/                       Optional GitHub proof images
README.md                          Setup and project overview
```

## Technology Stack

- **GitHub Pages frontend:** semantic HTML, custom CSS, vanilla JavaScript, SVG charts, Canvas animation, and checked-in JSON. It has no backend dependency and stores no visitor results.
- **Optional local backend:** Python 3.10+ and Flask 3 with SQLite storing derived results only.
- **Synthetic data:** Python standard library (`csv`, `random`) with a deterministic seed.
- **Tests:** pytest.

A React + FastAPI + PostgreSQL version would be suitable for a larger multi-user product, but adds build tooling, deployment, and identity/data-governance work. This student-friendly stack is easy to run and inspect. Neither version is a production deployment template.

## GitHub Pages — Independent Static Website

The deployable `github.io` website lives in `docs/`. It runs the complete questionnaire, scoring, category visualizations, recommendations, simulator, report, and checklist entirely in the browser. It makes no API calls, does not need Flask/SQLite/Node, and does not save visitor answers or scores. Assets and JSON paths are relative, so the site works at a repository URL such as `https://<username>.github.io/Social-Media-Privacy-Risk-Assessment/`.

The static data bundle is generated from the same Python questionnaire and scoring definitions:

```bash
python scripts/build_pages.py
python -m http.server 8001 --bind 0.0.0.0 --directory docs
```

Open `http://127.0.0.1:8001/` to test it as a static site. For deployment instructions, repository settings, and the exact public URL pattern, see [`docs/GITHUB_PAGES.md`](docs/GITHUB_PAGES.md). Enable GitHub Pages from **Settings → Pages → Deploy from a branch → `main` → `/docs`**.

## Privacy Questionnaire

Ten categories contain 56 questions: Profile Visibility (5), Personal Information (7), Location Privacy (6), Posts & Content (6), Friends / Followers (5), Tagging & Mentions (4), Authentication & Account Security (8), Third-Party Applications (4), Messaging & Social Engineering (6), and Digital Footprint (5).

Answers are fixed choices such as **YES / NO / SOMETIMES / NOT SURE**, **PUBLIC / FOLLOWERS-FRIENDS / PRIVATE**, or **NEVER / RARELY / SOMETIMES / OFTEN / NOT SURE**. Do not add free-text fields for sensitive profile data.

## Risk Categories

| Category | Weight |
|---|---:|
| Profile visibility | 10% |
| Personal information | 15% |
| Location privacy | 15% |
| Posts and content | 10% |
| Friends and followers | 10% |
| Tagging and mentions | 5% |
| Account security | 15% |
| Third-party applications | 5% |
| Social engineering | 10% |
| Digital footprint | 5% |
| **Total** | **100%** |

Each category uses a peak-aware educational score: **60% of the highest feature ratio + 40% of the category's average feature ratio**, normalized to 0–100. This prevents one serious issue (for example, real-time location exposure) from disappearing among several safer answers while still rewarding broader improvement. The overall score is the weighted average of category scores.

`YES` is not inherently risky for every question: a “control enabled” question scores the opposite way from an “exposure present” question. `NOT SURE` contributes a small review signal. The implementation and mappings are visible in `backend/services/questionnaire.py` and `backend/services/scoring_engine.py`.

Risk bands: **0–20 LOW · 21–40 MODERATE · 41–70 HIGH · 71–100 CRITICAL**. Higher means higher *assessed exposure* under this model. Weights, question wording, response mappings, and thresholds are educational assumptions; validate and calibrate them before any professional decision.

## Privacy Findings

Findings are generated only for answers with a nonzero model contribution. Each includes a static reason, category, severity, priority, and a practical recommendation. The engine does not claim to have detected a real exposed data item or verified a platform setting.

## Recommendation Engine

The recommendation engine deduplicates the associated advice and prioritizes **IMMEDIATE**, **IMPORTANT**, or **GOOD PRACTICE**. Examples include hiding unnecessary contact details, delaying travel updates until after leaving, enabling MFA, reviewing connected applications, and checking old public posts.

## Improvement Simulator

Select suggested changes such as limiting profile visibility, turning off broad location sharing, enabling tag review, enabling MFA, or reviewing third-party apps. The active mode copies enum answers in memory, applies only allow-listed safer values, and recalculates the model. It makes no changes to a real platform and stores no simulated answers. The result is a framework simulation—not a guarantee of safety.

## Digital Footprint

An **active footprint** includes content deliberately shared, such as posts and comments. A **passive footprint** can be generated or collected through online activity depending on the service and context. This project evaluates only self-reported review habits for old posts, comments, profile history, unused accounts, and settings. It does not search the web or track people.

## Social Engineering Awareness

Public context about an employer, school, travel, family references, interests, or events can sometimes make deceptive contact seem more credible. Defensive practice: pause, verify independently through a known channel, and never disclose a password, recovery code, or one-time verification code. This project contains no attack scripts or personalized targeting.

## Account Security

The assessment covers MFA, unique-password awareness, password reuse awareness (never the password itself), password-manager use, login alerts, recovery settings, active sessions, and unfamiliar-device review. Account security and privacy overlap—an account takeover may expose private content—but remain distinct categories.

## Privacy Dashboard

The overview page visualizes the synthetic cohort's score distribution, category averages, repeated privacy weaknesses, and self-reported account controls. The cohort contains 1,200 generated records with synthetic IDs only. It is not a live community or organization dashboard.

## Privacy Report

After an assessment, use **Open report** and then **Print / Save as PDF** in the browser. The report contains an ID, timestamp, derived scores, findings, recommendations, checklist, and disclaimer. It excludes questionnaire answers and sensitive identifiers.

## Privacy by Design

- **Data minimization:** ask whether information is visible, never collect the value.
- **Purpose limitation:** responses are used only for scoring and coaching.
- **Least privilege:** the app has no platform tokens, integrations, image access, or database of profile content.
- **Privacy by default:** local demo mode; no third-party analytics, trackers, remote fonts, or account connection.
- **Transparency:** scoring weights and answer mappings are documented in source.
- **User control:** voluntary assessment, reversible what-if simulation, report export, and delete route.
- **Retention limitation:** Flask mode stores derived results only and offers deletion; GitHub Pages mode stores nothing and clears answers on refresh/close.
- **Secure processing:** fixed-choice validation, small request size, SQL parameters, output escaping, security headers, and a basic in-memory API rate limit.

## Installation

Python 3.10 or newer is recommended. From this repository root:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python data/generate_dataset.py --count 1200 --seed 20251006
python -m backend.app
```

Open **http://127.0.0.1:8000**. The demo server binds to `0.0.0.0` so the workspace preview can reach it; it is intentionally not hardened for public deployment.

## Usage

1. Open the overview and synthetic dashboard.
2. Select **Start my assessment**.
3. Move through ten question groups. “Not sure” is available when needed.
4. Or select **Load fictional demo profile** to populate the fictional classroom scenario.
5. Select **Generate my readout** to score and view findings. The GitHub Pages build stores nothing; Flask stores derived output only.
6. Select or deselect proposed improvements and run the what-if simulation.
7. Open the printable report or download the privacy checklist.
8. In Flask mode choose **Delete saved result**; in Pages mode choose **Clear this readout** or refresh/close the tab.

## API Documentation

All JSON requests are same-origin. No account authentication is implemented because this is a local single-user educational demo. Do not expose it to untrusted users; a shared service would need authentication, authorization, TLS, secure deployment, consent/retention controls, and a stronger rate limiter.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Status and storage-mode note |
| `GET` | `/api/questionnaire` | 56 fixed-choice questions and category weights |
| `GET` | `/api/demo-profile` | Synthetic demo responses only |
| `GET` | `/api/improvements` | Allow-listed what-if actions |
| `POST` | `/api/assessment` | Validate, score, and store derived results |
| `GET` | `/api/assessment/{id}` | Retrieve derived result |
| `GET` | `/api/assessment/{id}/recommendations` | Retrieve recommendations |
| `POST` | `/api/assessment/simulate-improvement` | Calculate a non-persistent what-if result |
| `GET` | `/api/assessment/{id}/report` | Safe printable HTML report |
| `DELETE` | `/api/assessment/{id}` | Delete an assessment and child rows |
| `GET` | `/api/dashboard/stats` | Synthetic cohort aggregates + derived local count |
| `GET` | `/api/privacy-checklist` | Printable/downloadable checklist data |

Assessment request shape:

```json
{"responses": {"profile_visibility": "PUBLIC", "phone_public": "NO"}}
```

The example is intentionally abbreviated; the actual request must contain every known question ID and only approved enum values. Unknown fields (including contact details) and missing questions are rejected. Errors return JSON without echoing a submitted body.

## Testing

```bash
python -m pytest -q
```

The automated suite currently has 57 passing cases across Python scoring/API behavior and GitHub Pages bundle checks: questionnaire and score boundaries, validation, recommendations, simulation, data minimization, report escaping, security headers, API retrieval/deletion, relative assets, and the static-data contract.

## Security & Privacy Testing

- The schema has no columns for phone, email, address, birth date, password, exact location, private messages, or raw responses.
- The API accepts enum-only JSON; unexpected keys and free-text answers fail validation.
- The report HTML escapes dynamic fields; the client escapes displayed text.
- Flask sets `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, and a same-origin Content Security Policy.
- API request bodies are capped at 64 KiB and the demo has a basic in-memory per-IP rate limit.
- There are no user accounts or sessions in this local version; authentication/authorization are required before a shared deployment.
- The database can be deleted using the UI/API. Local database files are ignored by Git.

## Results

The fictional demo profile scores **57/100 — HIGH** under the model. Applying all suggested safer settings in the simulator moves the illustrative score to **0/100 — LOW** (57 points lower). This is a deterministic model result, not a measurement about a real person or a real-world safety guarantee.

## Limitations

- Self-reported answers are not independently verified.
- No platform-specific settings are fetched; platform labels and controls can vary.
- The score is a transparent educational heuristic, not calibrated incident probability.
- No face recognition, image upload, EXIF extraction, OCR, or location inference is performed. This is deliberate: a questionnaire-only first release avoids biometric or photo data collection.
- No real-profile JSON/CSV import, scraping, API proxy, account enumeration, or search is implemented.
- The local API has no authentication and should not be deployed publicly as-is.

## Future Improvements

Safe next steps: platform-specific privacy checklists, configurable organizational policies for consent-based workshops, privacy-awareness quizzes, maturity scoring, family/teen safety education, GRC exports, anonymous opt-in trend reporting, better human calibration, localization, accessibility review, report comparison over time with explicit consent, and a local-only browser build. Do not add scraping or invasive monitoring.

## Screenshots

Capture your own run and place reviewed images in `screenshots/`:

`01-folder-structure.png`, `02-architecture.png`, `03-home-dashboard.png`, `04-questionnaire-profile.png`, `05-questionnaire-location.png`, `06-account-security.png`, `07-overall-risk.png`, `08-category-radar.png`, `09-findings.png`, `10-recommendations.png`, `11-simulator-before-after.png`, `12-synthetic-cohort.png`, `13-checklist.png`, `14-printable-report.png`, `15-synthetic-dataset.png`, `16-automated-tests.png`, `17-database-schema.png`, `18-github-history.png`, `19-readme-preview.png`.

## Learning Outcomes

Questionnaire and API design, Python modularization, explainable risk scoring, synthetic data, frontend state management, SVG charts, local persistence, report generation, validation, privacy engineering, test design, Git workflows, and communicating limitations.

## GitHub Upload Strategy

Suggested repository name: `Social-Media-Privacy-Risk-Assessment`

**Description:** “Privacy-focused cybersecurity framework for assessing social-media exposure, account-security practices, social-engineering risk, digital-footprint risk, and personalized privacy improvements using synthetic/self-reported data.”

Suggested topics: `cybersecurity`, `privacy`, `social-media-privacy`, `privacy-risk`, `security-awareness`, `python`, `flask`, `digital-footprint`, `risk-assessment`, `grc`, `privacy-by-design`, `defensive-security`.

```bash
git init
git add .
git commit -m "Initialize social media privacy risk assessment"
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```

To publish the static website, go to **Settings → Pages → Deploy from a branch → main → /docs**. See [`docs/GITHUB_PAGES.md`](docs/GITHUB_PAGES.md) for the complete deployment instructions and URL format. The deployment does not need credentials in this workspace; push the repository from your own GitHub account.

Suggested incremental commits: `Create privacy assessment architecture`; `Add privacy questionnaire`; `Generate synthetic assessment dataset`; `Implement privacy feature extraction`; `Add category risk scoring`; `Implement overall privacy risk engine`; `Add privacy findings engine`; `Implement recommendation engine`; `Build privacy improvement simulator`; `Create privacy analytics dashboard`; `Add privacy assessment report`; `Implement privacy-by-design controls`; `Add automated privacy tests`; `Complete README and documentation`.

## Project Report and Threat Model

See [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md), [`docs/QUESTIONNAIRE.md`](docs/QUESTIONNAIRE.md), [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md), [`docs/PROJECT_GUIDE.md`](docs/PROJECT_GUIDE.md), [`docs/LOCAL_RUN.md`](docs/LOCAL_RUN.md), [`docs/GITHUB_PAGES.md`](docs/GITHUB_PAGES.md), [`docs/architecture.svg`](docs/architecture.svg), and [`docs/TEST_MATRIX.md`](docs/TEST_MATRIX.md) for the student report, all 56 prompts, defensive risk tables, beginner guide, step-by-step run commands, API notes, and test evidence.

## Ethical Disclaimer

> This project is designed for defensive cybersecurity and privacy education. It uses synthetic or voluntarily provided assessment responses and does not scrape, track, or profile real social-media users.
>
> Use the framework only for your own assessment or an explicitly authorized, consent-based workshop. Do not use the score to make hiring, admissions, disciplinary, insurance, or eligibility decisions. This educational framework is not legal advice, a security audit, or a guarantee that an account will or will not be compromised.

## Author

Student cybersecurity project — customize this section with your name, course, institution, and public repository link before publishing.
