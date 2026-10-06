# Test Matrix and Security/Privacy Verification

Executed on the project build with Python 3.13 and Flask 3.1.3 using `python -m pytest -q`.

**Latest recorded run:** `57 passed in 0.27s`. “Actual” below means the assertion passed in that run; rerun locally after code changes to produce fresh evidence.

## Functional and privacy test cases

| ID | Scenario | Input / fixture | Expected result | Actual result | Status |
|---|---|---|---|---|---|
| T01 | Fully private profile | All safest enum choices | Score 0, LOW, no findings | 0 / LOW / no findings | PASS |
| T02 | Fictional public demo profile | `safe_demo_responses()` | Elevated, explainable risk | 57 / HIGH, 12 findings | PASS |
| T03 | Public phone | `phone_public=YES` | Personal-info score increases | Increased | PASS |
| T04 | Public email | `email_public=YES` | Personal-info score increases | Increased | PASS |
| T05 | Full birthday public | `birthday_public=YES` | Personal-info score increases | Increased | PASS |
| T06 | Workplace exposure | `workplace_public=YES` | Personal-info score increases | Increased | PASS |
| T07 | Education exposure | `education_public=YES` | Personal-info score increases | Increased | PASS |
| T08 | Real-time location | `current_location_public=YES` | Location category becomes high | Score ≥ 60 | PASS |
| T09 | Real-time check-in | `checkins_enabled=YES` | Location category becomes high | Score ≥ 60 | PASS |
| T10 | Travel plans public | `travel_plans_public=YES` | Location category becomes high | Score ≥ 60 | PASS |
| T11 | Public post audience | `posts_public=YES` | Content score increases | Increased | PASS |
| T12 | Unknown connections | `accept_unknown_connections=OFTEN` | Connection finding generated | Finding present | PASS |
| T13 | Tag review disabled | `tag_review_enabled=NO` | Tagging risk is non-zero | Non-zero | PASS |
| T14 | MFA disabled | `mfa_enabled=NO` | Immediate MFA action generated | Immediate action present | PASS |
| T15 | Login alerts disabled | `login_alerts_enabled=NO` | Finding generated | Finding present | PASS |
| T16 | Password reuse reported | `password_reuse_reported=YES` | Risk finding; no password requested | Finding present | PASS |
| T17 | Apps not reviewed | `third_party_apps_reviewed=NO` | Third-party score is non-zero | Non-zero | PASS |
| T18 | Unexpected links | `clicks_unexpected_links=OFTEN` | Social-engineering finding generated | Finding present | PASS |
| T19 | Old posts not reviewed | `old_posts_reviewed=NO` | Digital-footprint finding generated | Finding present | PASS |
| T20 | Privacy settings not reviewed | `privacy_settings_reviewed=NO` | Digital-footprint finding generated | Finding present | PASS |
| T21 | Feature extraction structure | Safe response map | All 56 features and 10 category totals returned | 56 / 10 | PASS |
| T22 | Overall weighted score | Profile score 100, all others 0 | Default profile weight gives 10 | 10 | PASS |
| T23 | LOW upper boundary | Score 20 | LOW | LOW | PASS |
| T24 | MODERATE upper boundary | Score 40 | MODERATE | MODERATE | PASS |
| T25 | HIGH upper boundary | Score 70 | HIGH | HIGH | PASS |
| T26 | CRITICAL lower boundary | Score 71 | CRITICAL | CRITICAL | PASS |
| T27 | Personalized recommendation | Public phone visibility | Advice matches the affected field | Number-visibility advice present | PASS |
| T28 | Improvement simulator | Fictional demo + approved actions | Simulated score lower; no real settings changed | 57 → 10; reduction 47 | PASS |
| T29 | Database save and retrieval | Synthetic assessment result | Derived score/categories retrievable | Score and 10 categories retrieved | PASS |
| T30 | Sensitive-data schema review | SQLite `PRAGMA table_info` | No raw answers or PII columns | Only derived assessment columns | PASS |
| T31 | Report generation | Synthetic assessment result | Scores, actions, checklist, print affordance included | Required sections present | PASS |
| T32 | Report XSS escaping | Assessment ID containing `<script>` | Markup escaped, not executed | Escaped | PASS |
| T33 | Missing answer validation | Remove `phone_public` | Reject request with validation error | `ValueError` raised | PASS |
| T34 | Extra sensitive field | Add `phone_number` | Reject unknown field | `ValueError` raised | PASS |
| T35 | Free-text answer | Put contact-like sentence in enum field | Reject non-enum input | `ValueError` raised | PASS |
| T36 | Simulator allow-list | Include unknown change ID | Reject unsafe change | `ValueError` raised | PASS |
| T37 | Privacy checklist | Checklist payload | At least 18 items | 19 items | PASS |
| T38 | API create/read | Valid fictional response map | Create 201; GET returns derived result only | 201 + successful derived-only GET | PASS |
| T39 | API contact field rejection | Add email field to answers | HTTP 400; no input echo | HTTP 400 | PASS |
| T40 | API simulator | Demo + selected approved changes | HTTP 200 and score reduction | HTTP 200, lower score | PASS |
| T41 | API report route | Created synthetic assessment ID | HTML report without raw answers | HTML returned; no response payload | PASS |
| T42 | Assessment deletion | Create then DELETE | Saved result becomes unavailable | DELETE 200; GET 404 | PASS |
| T43 | Security response headers | Health endpoint | Security headers set | `nosniff`, `DENY`, geolocation disabled | PASS |
| T44 | Questionnaire coverage | Questionnaire API | At least 40 questions, ten categories | 56 questions, ten groups | PASS |
| T45 | Fictional demo preset | Demo endpoint | Marked fictional, no username field | Fictional + 56 enum choices | PASS |
| T46 | API rate limit | Limit temporarily set to 2 | Third request returns 429 | 200, 200, 429 | PASS |
| T47 | Session behavior | Health endpoint | No browser session cookie | No `Set-Cookie` | PASS |
| T48 | Cascade deletion | Delete parent assessment | Category and finding rows removed | Both child counts 0 | PASS |
| T49 | Environment configuration | Set `DATABASE_PATH` environment variable | App uses configured path | Configured SQLite file created | PASS |
| T50 | Fully exposed fictional profile | Highest-risk enum for all questions | 100 / CRITICAL across categories | 100 / CRITICAL; all categories 100 | PASS |
| T51 | Pages static bundle | Required HTML, CSS, JS, JSON, `.nojekyll` | All publish files exist | All present | PASS |
| T52 | Pages questionnaire contract | Static framework JSON | 56 questions / ten categories | 56 / ten | PASS |
| T53 | Pages demo fixture | Static demo JSON vs Python fixture | Identical fictional enum answers | Identical | PASS |
| T54 | Pages simulator allow-list | Static map vs Python safe map | Same approved safe values | Same | PASS |
| T55 | Pages URL paths | `index.html` references | CSS/JS URLs are relative | Relative paths found | PASS |
| T56 | Pages backend independence | Static JavaScript source | No `/api/`, localhost, or `127.0.0.1` call | No API/loopback references | PASS |
| T57 | Pages cohort data | Static aggregate JSON | 1,200 synthetic records; no usernames or recent rows | Synthetic aggregate only | PASS |

## Security and privacy verification notes

1. **Data minimization:** `assessments` contains only ID, score, level, and timestamp. Category, finding, and recommendation tables contain derived content. Tests inspect schema; no response JSON is persisted.
2. **Input validation:** known question IDs and known enum choices only; unknown keys, missing questions, invalid values, and extra fields are rejected. No free-text answer is accepted.
3. **XSS:** HTML report escapes dynamic fields. Browser rendering escapes strings before inserting them into result markup. Continue testing if user-controlled fields are ever introduced.
4. **Rate limiting:** an in-memory per-IP limit is implemented and tested. It is an educational safeguard, not production-grade or distributed rate limiting.
5. **Authentication / authorization:** not implemented because there are no user accounts. This is a local single-user demo. Do not expose it as a shared service. A real multi-user version needs authenticated ownership checks for read/delete, secure sessions or token handling, TLS, CSRF-aware design, and privacy governance.
6. **Session handling:** the app does not create a session or cookie; a test verifies no `Set-Cookie` header. Do not add session state without secure cookie flags and threat modeling.
7. **Environment variables:** `DATABASE_PATH` and `PORT` are read by the server; the example config is `.env.example`. The project does not implicitly parse `.env`; export values in the shell.
8. **Safe report:** no responses, identifiers, contact values, passwords, photos, or location values are included. The report is HTML and can be printed to PDF in the browser.
9. **Deletion:** the API deletes the assessment parent; SQLite foreign-key cascades remove categories, findings, and recommendations.
10. **Synthetic data:** the only cohort records are generated locally by `data/generate_dataset.py` with no names, accounts, posts, or real contact/location values.

## Running the test suite

```bash
python -m pytest -q
```

For public evidence, capture the terminal output and include it as `screenshots/27-pytest-results.png`. Test results should be regenerated from the exact commit you publish.
