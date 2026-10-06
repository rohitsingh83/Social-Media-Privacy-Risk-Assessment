# Student Project Guide — PRIVACY//FIELD

## 1. Project explanation

### Simple explanation

PRIVACY//FIELD is a privacy checkup, not a profile inspector. A person answers questions about their settings and habits—such as whether contact details are public, whether MFA is on, and whether old posts are reviewed. The program converts the answers into a risk score, explains the biggest areas to review, and gives practical next steps. It never logs in to a social network or asks for the underlying sensitive details.

### Technical explanation

The browser requests a fixed 56-item questionnaire from Flask. Every submitted value is checked against an allow-list of question IDs and enum options. `extract_privacy_features()` converts answers to per-feature risk points in memory. Each of ten categories becomes a 0–100 score. A weighted scoring engine computes the overall risk and classifies the result. Findings and recommendations are derived from static question metadata. The database stores only the derived score, risk level, category scores, finding types, and recommendation text. The original response object is discarded after request processing.

```text
User
  ↓
Privacy Questionnaire
  ↓
Input Validation (known fields + approved choices)
  ↓
Privacy Feature Extraction (memory only)
  ↓
Category Risk Analysis
  ↓
Weighted Risk Scoring Engine
  ↓
Risk Classification (LOW / MODERATE / HIGH / CRITICAL)
  ↓
Personalized Findings + Recommendations
  ↓
Privacy Dashboard + What-if Simulator + Report
```

### Key terms

- **Social-media privacy:** control over which personal information is exposed, to whom, and how it may be used.
- **Digital footprint:** information associated with an online presence. An **active** footprint includes deliberate posts and comments; a **passive** footprint can be generated or collected by services depending on context. This app evaluates only self-reported review habits.
- **Personal-information exposure:** making details such as contact information, full birthday, home-related clues, workplace, education, or family information broadly visible. The app asks only whether this happens.
- **Oversharing:** revealing more personal context, timing, or detail than is needed for the intended audience or purpose.
- **Social engineering:** manipulation that pressures a person to disclose information or take an unsafe action. Public context can make a deceptive request feel plausible; verify independently.
- **Identity-related risk:** information exposure may increase the risk of impersonation, unwanted correlation, account recovery abuse, or other misuse. Risk depends on context; disclosure does not mean harm will occur.
- **Location exposure:** real-time sharing, geotags, check-ins, travel timing, or recurring patterns may reveal whereabouts or routines. Posting after leaving can reduce immediate exposure compared with broadcasting in real time, but it does not erase all context.
- **Historical posts:** content can remain visible after an intended audience, job, school, relationship, or personal preference has changed. Review the audience and remove or limit content that no longer fits.
- **Regular privacy reviews:** platforms change controls and defaults. Recheck profile visibility, tags, connected applications, sessions, and older posts periodically.
- **MFA:** multi-factor authentication adds another proof of identity beyond a password and can reduce some account-takeover risks. It does not hide public information or make every attack impossible.

## 2. Industry relevance and roles

The framework maps to cybersecurity and privacy work through exposure review, defensive risk prioritization, least-privilege guidance, security-awareness coaching, secure API/data handling, and evidence-based documentation.

| Discipline / role | Connection to this project |
|---|---|
| Cybersecurity Analyst | Turns a structured set of signals into explainable risk and mitigation actions. |
| Privacy Analyst / Privacy Engineer | Applies data minimization, purpose limitation, transparency, retention limits, and user control. |
| GRC Analyst | Documents a rubric, controls, assumptions, limitations, and a repeatable review process. |
| SOC Analyst | Practices prioritization and clear findings; this project is not a SOC detection feed. |
| Security Consultant | Communicates practical, consent-based recommendations and risk context. |
| IAM Analyst | Evaluates MFA, recovery, sessions, device review, and sign-in integrations. |
| Security Awareness Specialist | Delivers short, behavior-focused coaching rather than attack instructions. |
| Application Security Analyst | Validates strict schemas, uses parameterized SQL, applies output escaping, headers, and tests. |

Possible applications are voluntary student orientation, creator/SMB self-checks, and family safety education. Avoid involuntary employee or applicant scoring. Do not use this prototype for hiring, school admission, discipline, or eligibility decisions.

## 3. Privacy versus security

Privacy controls **what is shared and with whom**. Security controls **who can access or change an account/system**.

Examples:

1. A unique password plus MFA can protect account access, while public profile fields still expose a phone number. Security improved; privacy did not.
2. A private profile can reduce audience exposure, but a reused password can still make account takeover more likely. Privacy improved; authentication hygiene did not.
3. Tag review limits what appears on a profile, but it cannot guarantee that another person will not share content elsewhere. Controls reduce exposure; they are not absolute.

## 4. Visibility, location, photos, and context

Visibility is not automatically unsafe. Public posts may be intentional for creators, organizations, or public-interest work. The key question is whether the audience matches the purpose and whether the content contains more detail than intended. This questionnaire asks about public visibility, search discoverability, follower lists, activity indicators, and post audiences.

Photo risk is broader than EXIF. An image can show location context, a workplace or school, a vehicle identifier, a badge, documents, a computer screen, family members, or travel timing. EXIF is a family of metadata fields that some image formats may include (for example, device make/model, timestamps, and sometimes coordinates). Platforms may strip some metadata; do not assume every service does. This version **does not upload, inspect, infer from, or process images**. A later local-only metadata-copy tool should be separately reviewed for consent, safe file handling, and metadata removal correctness; it should never infer hidden location.

## 5. Social engineering awareness

A public employer, college, travel plan, family reference, hobby, or event may add context that makes an impersonation or phishing attempt seem more believable. The defensive response is conceptual and simple: pause, use a known independent channel to confirm, navigate to the official service directly, and never relay a one-time code. This project has no attack scripts, target lookups, or personalized message generation.

## 6. Account security and third-party apps

The account category covers MFA, unique-password awareness, password reuse awareness, password-manager use, login alerts, recovery review, active sessions, and device review. The app never accepts passwords or recovery data. Privacy and security overlap because takeover may expose private content, but account protection is not the same as reducing public exposure.

Third-party integrations and “sign in with” links can retain access after a user stops using them. **Least privilege** means granting only the permissions needed for the current purpose. Review connections, remove unused apps, and narrow permissions where possible. The app does not read the integrations list.

Tagging is another person's ability to expose context about you. Tag review, mention limits, and audience controls can reduce profile-level exposure, but cannot control every copy or repost made elsewhere.

## 7. Questionnaire and feature engineering

There are 56 questions across ten categories: profile (5), personal information (7), location (6), content (6), connections (5), tagging (4), account security (8), third-party apps (4), social engineering (6), and digital footprint (5). The full prompt, choices, and risk map are in `backend/services/questionnaire.py`; the UI receives only prompt/help/options, not scoring internals.

`extract_privacy_features(responses)` returns an in-memory structure containing feature ID, category, points, maximum points, risk ratio, and category totals. High exposure and disabled controls contribute risk. For a behavior question, frequency choices are ordered from lower to higher risk. “Not sure” adds a small review signal rather than being treated as safe or as proof of exposure.

## 8. Scoring and interpretation

For each category:

```text
feature ratio = risk points / feature maximum
category score = (0.60 × highest feature ratio + 0.40 × average feature ratio) × 100
```

The peak-aware blend allows one severe exposure to be visible in its category; the mean rewards broad improvements. The overall score is a weighted average of ten category scores. The configured weights total 100%: 10, 15, 15, 10, 10, 5, 15, 5, 10, 5. The levels are LOW 0–20, MODERATE 21–40, HIGH 41–70, CRITICAL 71–100.

These values are transparent educational assumptions—not incident likelihood, breach probability, certification, or a guarantee that an account will or will not be compromised. A professional risk model needs expert review, representative consent-based benchmarks, documented use context, bias analysis, calibration, and periodic validation.

## 9. Synthetic dataset

`data/generate_dataset.py` creates 1,200 synthetic records by default using a fixed random seed. It generates enum selections and risk scores from the same assessment engine, writes only synthetic IDs such as `SYN-000001`, and stores no names, profile handles, real contact values, post text, or locations. Regenerate with:

```bash
python data/generate_dataset.py --count 1200 --seed 20251006
```

The CSV has the requested fields (`profile_id`, visibility and exposure flags, controls, score, and level) plus ten category-score columns used for the charts. `profile_id` is a synthetic sequence, not an identifier for a person.

## 10. Safe demonstration profile

The built-in demo is fictional and reflects the brief: public profile; phone and full birthday visibility reported; location/check-in and travel posts reported; unfamiliar requests often accepted; tag review, MFA, login alerts, third-party review, and old-post review disabled. Email is private. It currently produces **57/100, HIGH** with these category scores:

| Category | Score |
|---|---:|
| Profile visibility | 68 |
| Personal information | 71 |
| Location privacy | 80 |
| Posts and content | 0 |
| Friends and followers | 68 |
| Tagging and mentions | 70 |
| Account security | 70 |
| Third-party applications | 70 |
| Social engineering | 0 |
| Digital footprint | 68 |

Top findings include the profile visibility, public phone/birthday, real-time location/check-ins/travel timing, unknown requests, tag review, MFA, login alerts, app review, and older posts. The simulator starts with approved actions matching those findings selected. Applying the full suggested set moves the illustrative score from 57 to 0 (LOW), a 57-point model reduction. Because the simulator recalculates only the framework model, it must not be described as a real-world safety guarantee.

## 11. Data storage and database schema

SQLite tables:

- `ASSESSMENTS(assessment_id, overall_score, risk_level, created_at)`
- `CATEGORY_SCORES(category_score_id, assessment_id, category, score, weight)`
- `FINDINGS(finding_id, assessment_id, category, finding_type, severity, description)`
- `RECOMMENDATIONS(recommendation_id, assessment_id, finding_type, recommendation, priority)`

No raw `responses` column exists. There are no columns for contact data, account handles, passwords, private messages, or exact locations. Foreign-key cascades support deletion. SQL is parameterized.

## 12. REST API contract

| Method / endpoint | Request | Successful response | Validation / privacy |
|---|---|---|---|
| `GET /api/questionnaire` | none | Groups, approved options, 56-question count | No user data. |
| `GET /api/demo-profile` | none | Fictional enum-only answers | Clearly labelled synthetic. |
| `POST /api/assessment` | `{ "responses": { all_known_question_ids: approved_enum } }` | 201 + ID, category scores, findings, recommendations | Only `responses` allowed; missing/unknown IDs and free text rejected; answers not stored. |
| `GET /api/assessment/{id}` | opaque random ID | Derived result | No answer payload returned. |
| `GET /api/assessment/{id}/recommendations` | opaque random ID | Recommendation list | No profile data. |
| `POST /api/assessment/simulate-improvement` | `{ "responses": {...}, "changes": [approved_id] }` | Current/simulated score and delta | Strict enum validation; server-side allow-list; not persisted. |
| `GET /api/dashboard/stats` | none | Synthetic cohort aggregates and stored-result count | No per-person listing. |
| `GET /api/privacy-checklist` | none | Checklist items | Static content. |
| `GET /api/assessment/{id}/report` | opaque random ID | Escaped printable HTML | Derived results only. |
| `DELETE /api/assessment/{id}` | opaque random ID | `{ "deleted": true }` | Deletes parent and dependent rows. |

Errors use JSON `400` for invalid payload, `404` for unknown ID, `413` for oversized request, `415` for non-JSON assessment calls, and `429` for rate limit. Authentication and authorization are not implemented; this is a local single-user demo. A shared version needs accounts or access controls, TLS, CSRF-aware design, production rate-limiting, monitoring that does not log bodies, consent, retention policy, and deployment review.

## 13. Project structure

```text
Social-Media-Privacy-Risk-Assessment/
├── backend/
│   ├── app.py                         Flask app factory, static routes, security headers
│   ├── routes/api.py                  REST API blueprint and request validation
│   ├── models/database.py             Derived-only SQLite schema
│   └── services/
│       ├── questionnaire.py           56 questions, response maps, demo, safe actions
│       ├── scoring_engine.py           Validation, feature extraction, scoring
│       ├── assessment_engine.py        Assessment orchestration
│       ├── findings_engine.py          Explainable findings
│       ├── recommendation_engine.py    Prioritized coaching
│       ├── improvement_simulator.py    Allow-listed what-if changes
│       ├── dashboard_analytics.py      Synthetic cohort aggregates
│       └── reporting.py                Printable report and checklist
├── frontend/
│   ├── index.html                     Single-page dashboard shell
│   └── assets/                        CSS animations, client interactions, report JS
├── data/
│   ├── generate_dataset.py            Deterministic synthetic generator
│   └── social_media_privacy_assessments.csv
├── docs/
│   ├── index.html                     Independent GitHub Pages website entrypoint
│   ├── assets/                        Static client-only scorer and animated CSS
│   ├── data/                           Generated questionnaire/demo/checklist/cohort JSON
│   └── *.md                            Guide, report, deployment, threat model, tests
├── scripts/build_pages.py             Regenerate backend-free Pages data bundle
├── tests/test_assessment.py           Automated engine/API/privacy tests
├── tests/test_pages.py                Static Pages bundle checks
├── reports/                           Optional student-generated outputs
├── screenshots/                       Optional GitHub proof images
├── instance/                          Local SQLite file (ignored by Git)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 14. Stack options

**Beginner option:** HTML/CSS/JavaScript + Flask + SQLite + inline SVG. Low setup cost and easy to audit; less suitable for multi-user scale.

**Modern option:** React/Vite + FastAPI + PostgreSQL + Recharts. Stronger component ecosystem and typing; requires a build tool, dependency maintenance, authentication, database deployment, and more privacy/security controls. This project keeps the beginner-friendly Flask API for local learning and also ships a separate static GitHub Pages build that needs no backend.

## 15. Privacy checklist

- [ ] Review profile visibility and search discoverability.
- [ ] Hide unnecessary contact information and full birth-date visibility.
- [ ] Review workplace, education, family, and relationship details.
- [ ] Review location sharing, geotags, check-ins, and routine patterns.
- [ ] Avoid unnecessary real-time location and travel announcements.
- [ ] Review who can see posts, followers, and connection lists.
- [ ] Restrict tagging and enable approval before tags appear.
- [ ] Verify unfamiliar connection requests before accepting them.
- [ ] Enable MFA using a strong supported method.
- [ ] Use unique passwords; consider a password manager.
- [ ] Enable login alerts and review recovery options.
- [ ] Review active sessions and unfamiliar devices.
- [ ] Review connected third-party apps and remove unused integrations.
- [ ] Apply least privilege to permissions granted to connected apps.
- [ ] Review photo framing and metadata before sharing.
- [ ] Pause before opening unexpected links or acting on urgent messages.
- [ ] Never share one-time verification codes or recovery codes.
- [ ] Review older public posts, comments, profile history, and unused accounts.
- [ ] Schedule a privacy-settings review every few months.

## 16. Privacy by Design controls in the application

**Data minimization:** the form contains only enum choices. **Purpose limitation:** answers drive the requested report only. **Least privilege:** no platform permissions or tokens. **Privacy by default:** no account connection, external resources, image upload, or tracking. **Transparency:** source and weights are inspectable. **User control:** voluntary assessment, local simulation, report export, and delete action. **Retention limitation:** only derived results persist. **Secure processing:** strict validation, output escaping, bounded requests, parameterized SQL, headers, and tests.

## 17. GitHub publication strategy

Repository: `Social-Media-Privacy-Risk-Assessment`.

Suggested first commands:

```bash
git init
git add .
git commit -m "Initialize social media privacy risk assessment"
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```

Suggested topic tags: `cybersecurity`, `privacy`, `social-media-privacy`, `privacy-risk`, `security-awareness`, `python`, `flask`, `digital-footprint`, `risk-assessment`, `grc`, `privacy-by-design`, `defensive-security`.

Suggested commits: `Create privacy assessment architecture`; `Add privacy questionnaire`; `Generate synthetic assessment dataset`; `Implement privacy feature extraction`; `Add category risk scoring`; `Implement overall privacy risk engine`; `Add privacy findings engine`; `Implement recommendation engine`; `Build privacy improvement simulator`; `Create privacy analytics dashboard`; `Add privacy assessment report`; `Implement privacy-by-design controls`; `Add automated privacy tests`; `Complete README and documentation`.

## 18. Proof-of-work screenshot checklist

Use real screenshots from your own run; redact machine-specific path or account details if any appear. Suggested filenames:

1. `01-project-folder-structure.png`
2. `02-system-architecture.png`
3. `03-home-hero-animation.png`
4. `04-synthetic-cohort-dashboard.png`
5. `05-profile-visibility-questionnaire.png`
6. `06-personal-information-questionnaire.png`
7. `07-location-privacy-questionnaire.png`
8. `08-content-and-metadata-awareness.png`
9. `09-connections-and-tagging.png`
10. `10-account-security-questionnaire.png`
11. `11-third-party-apps-questionnaire.png`
12. `12-social-engineering-questionnaire.png`
13. `13-digital-footprint-questionnaire.png`
14. `14-overall-risk-score.png`
15. `15-category-risk-radar.png`
16. `16-top-findings.png`
17. `17-personalized-recommendations.png`
18. `18-simulator-before.png`
19. `19-simulator-after.png`
20. `20-risk-reduction-delta.png`
21. `21-risk-distribution-chart.png`
22. `22-top-weaknesses-chart.png`
23. `23-security-controls-chart.png`
24. `24-privacy-checklist-download.png`
25. `25-printable-assessment-report.png`
26. `26-synthetic-csv-preview.png`
27. `27-pytest-results.png`
28. `28-database-schema.png`
29. `29-github-commits-and-readme.png`

## 19. Resume and LinkedIn

### Resume bullets

- Built a consent-based social-media privacy assessment in Python/Flask with a 56-question questionnaire, strict enum validation, ten explainable category scores, configurable weighted scoring, and prioritized remediation.
- Generated a deterministic 1,200-row synthetic dataset and created an animated JavaScript/SVG dashboard, printable report, privacy checklist, and what-if improvement simulator.
- Applied privacy-by-design and application-security controls: no profile scraping or raw PII fields, derived-only SQLite persistence, output escaping, bounded API requests, security headers, deletion, and 57 automated tests.

### Two-line description

A privacy-first cybersecurity framework that helps people review social-media exposure and account-security habits without connecting to, scraping, or profiling accounts. Includes category-wise scoring, explainable coaching, synthetic analytics, a safe improvement simulator, and a derived-only report.

### LinkedIn project description

I built PRIVACY//FIELD, a defensive social-media privacy self-assessment for cybersecurity education. Users answer fixed-choice questions about visibility, personal-information exposure, location habits, posts, connections, tagging, authentication, third-party apps, social engineering, and digital-footprint reviews. The app returns a transparent 0–100 educational risk score, ten category scores, findings, prioritized recommendations, a what-if simulator, and a printable report. It uses Flask, Python, SQLite, HTML/CSS/JavaScript, SVG visualizations, generated fictional data, and pytest. It does not scrape, track, or access real profiles and does not collect phone numbers, passwords, addresses, exact locations, photos, or private messages. Risk weights are educational assumptions, not a compromise prediction.

### Skills demonstrated

Cybersecurity · Privacy Risk Assessment · Privacy by Design · Digital Footprint Analysis · Social Engineering Awareness · Risk Scoring · Python · Flask · SQLite · Data Analytics · Security Awareness · GRC Concepts · Input Validation · API Testing · Synthetic Data Engineering.

### GitHub repository description

“Privacy-focused cybersecurity framework for assessing social-media exposure, account-security practices, social-engineering risk, digital-footprint risk, and personalized privacy improvements using synthetic/self-reported data.”

## 20. Future improvements

Platform-specific user-facing privacy checklists; configurable policies for consent-based workshops; privacy-awareness quizzes; maturity scoring; family/teen safety learning modules; enterprise awareness training without individual surveillance; GRC reporting; anonymous opt-in trend analysis; validation and calibration with expert-reviewed synthetic/consented samples; localization; accessibility; user-controlled comparison over time; and an optional local-only build. Avoid scraping, hidden monitoring, or automated person-level profiling.

## 21. Interview preparation — exactly 10 questions and answers

### 1. “Explain your project.”
I built a social-media privacy risk self-assessment that does not scrape profiles or connect to accounts. Users answer a 56-question fixed-choice questionnaire about privacy settings and security habits. The Python engine converts the choices into ten category scores, a weighted overall score, explainable findings, and prioritized recommendations. I added a fictional synthetic dashboard, a safe what-if simulator, report generation, and tests. The system stores only derived results and never asks for contact details, passwords, exact locations, photos, or private messages.

### 2. “What is the difference between privacy and security?”
Privacy is about how information is exposed, shared, and used. Security protects accounts, systems, and information from unauthorized access or misuse. They overlap but are not equivalent: MFA can strengthen account security while a public phone number or location post remains a privacy exposure.

### 3. “What is a digital footprint?”
It is information associated with a person's online presence. Active footprint includes content they deliberately share; passive data may be generated or collected by a service depending on context. My project assesses only self-reported review practices and does not search for or track anyone.

### 4. “How can oversharing affect social-engineering risk?”
Public context about a workplace, school, travel, family, interests, or events can sometimes make deceptive contact appear more credible. The defensive response is to pause, independently verify through a known channel, navigate to official sites directly, and never share authentication codes. I do not generate attack messages.

### 5. “How does the scoring model work?”
Each answer maps to fixed risk points. Within each category, I blend the highest feature risk at 60% with the category average at 40%, then normalize to 0–100. The ten category scores are combined using weights that total 100%. Higher means higher assessed exposure. The weights and thresholds are educational assumptions that need calibration before professional decisions.

### 6. “Why did you include MFA in a privacy tool?”
If an account is taken over, private messages, photos, contacts, or recovery options could be affected. MFA adds a second factor and can reduce some account-takeover risk. It belongs in account security, which is related to but separate from public-information exposure.

### 7. “What risks can third-party applications create?”
Connected applications may retain permissions after a user stops needing them. I ask whether the user reviews integrations and uses only permissions required for their purpose. This applies least privilege; the application does not query the real account's app list.

### 8. “How did you apply Privacy by Design?”
The form asks whether information is visible rather than collecting the information itself. It has no phone, email, address, birth-date, password, location, image, or message field. Answers are processed in memory, the database stores derived scores and finding types, and the user can delete the result. I also documented limitations and uses.

### 9. “What does the improvement simulator do?”
It takes the in-memory answers, applies only predefined safer settings to a temporary copy, and runs the same scoring function again. It does not modify a social account or save the simulated answers. I label the delta as a framework simulation, not a guarantee of real-world safety.

### 10. “How did you test it and what would you improve?”
I wrote automated tests for safe and risky synthetic answers, category score changes, risk boundaries, validation, recommendation generation, simulation, SQLite fields, report escaping, API responses, headers, and deletion. I would next improve accessibility and localization, calibrate the model with expert-reviewed consent-based scenarios, and create platform-specific checklists. I would not add scraping or covert monitoring.
