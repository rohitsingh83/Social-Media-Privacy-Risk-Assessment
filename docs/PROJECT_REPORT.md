# Project Report: Social Media Privacy Risk Assessment Framework

## Abstract

This project presents PRIVACY//FIELD, a defensive, consent-based framework for helping a person review their social-media privacy settings and account-security habits. A fixed-choice questionnaire covers ten categories, including profile visibility, personal information, location, content, connections, tagging, authentication, third-party applications, social engineering, and digital footprint. The Python engine performs strict input validation, feature extraction, category scoring, weighted overall classification, finding generation, recommendation prioritization, and a non-persistent improvement simulation. A responsive browser dashboard visualizes the results and a separate fictional 1,200-record dataset. The database stores derived outcomes only. The prototype does not scrape profiles, access private accounts, collect contact values or passwords, analyze images, or track people. Its rubric is educational and is not a compromise prediction or professional risk certification.

## 1. Introduction

Social-media platforms support communication, learning, business, and public engagement. Their settings and sharing features can also expose more information than a user intends. Users may not realize how profile visibility, social connections, old posts, location practices, tags, authentication controls, or third-party permissions combine. This framework translates privacy awareness into a repeatable self-review and a prioritized improvement plan.

## 2. Problem Statement

Privacy controls are spread across platform settings, may change over time, and can be difficult for a beginner to interpret. A user may strengthen account authentication without limiting public personal information, or restrict a profile while overlooking connected applications and historic content. A privacy-first educational tool is needed to help users inspect their own practices without surveillance or unnecessary collection.

## 3. Objectives

1. Create a structured questionnaire with at least 40 questions; this implementation contains 56.
2. Evaluate ten privacy and account-safety categories using a transparent rubric.
3. Return a 0–100 score, risk band, category scores, findings, and personalized actions.
4. Provide an interactive improvement simulator clearly labelled as a model-only simulation.
5. Generate an HTML report and a downloadable privacy checklist.
6. Demonstrate synthetic data analytics, safe persistence, REST API validation, and automated tests.
7. Keep the system defensive and do not scrape, enumerate, identify, or track people.

## 4. Social-Media Privacy Background

Social-media privacy concerns the exposure, audience, and use of information shared or associated with online accounts. A user's public profile, posts, photos, follower list, activity signals, tags, linked services, and historical content can each reveal different context. No single privacy setting is a complete safety control; users should choose audiences based on purpose and review settings periodically.

Personal-information exposure includes visibility of contact details, a full birth date, home-related clues, workplace or education details, and family or relationship information. The questionnaire asks only whether these details are visible. It never requests the underlying values.

Oversharing means communicating more detail, timing, or context than is appropriate for the intended audience. Its effect depends on context and does not imply that an incident will occur.

## 5. Digital Footprint

An active digital footprint is information a person deliberately publishes, such as posts, comments, photos, and profile details. A passive footprint can be generated or collected by services through ordinary interactions, depending on service context. This project does not search for passive data or collect browsing activity. It asks whether a participant reviews old posts, public comments, profile history, unused accounts, and settings.

Historical posts matter because an audience, purpose, job, school, or preference can change while older material remains accessible. Regular reviews can align existing content with the user's present intent.

## 6. Privacy vs Security

Privacy controls how information is collected, exposed, shared, and used. Security protects systems, accounts, and information from unauthorized access or misuse. Strong authentication can reduce some account-takeover scenarios, but it does not make a public profile private. Conversely, a limited audience does not prevent a weak or reused password from being abused. The categories overlap because account compromise can affect private content, but they remain distinct assessment areas.

## 7. Social Engineering

Social engineering uses persuasion or deception to influence a person into disclosing information or taking an unsafe action. Public context about an employer, school, travel, family, interests, or events can sometimes make fraudulent communications seem more plausible. Defensive guidance in this project is conceptual: pause, verify independently through a known channel, avoid unexpected links, and never share verification codes. No attack instructions or personalized pretexts are generated.

## 8. Existing Approaches and Proposed Framework

Common user approaches include reviewing platform settings manually, using general security checklists, or relying on automated footprint scanners. Manual reviews can be difficult to repeat; intrusive scanners can collect more information than necessary. PRIVACY//FIELD proposes a deliberately limited alternative: a self-reported questionnaire with explainable rules, derived-only persistence, clear limitations, and no platform connection.

The initial version does not parse exported platform files. This is a deliberate scope choice: a questionnaire-only flow demonstrates the core privacy framework without handling raw profile text, photos, contact information, or private exports. A future local-only importer would require separate threat modeling and explicit consent.

## 9. System Architecture

```text
Browser UI
  → Fixed-choice questionnaire
  → Flask API input validation
  → In-memory feature extraction
  → Ten category analyzers
  → Weighted score and risk classification
  → Findings and recommendations
  → SVG dashboard, simulator, printable report

Synthetic CSV → aggregate dashboard analytics

SQLite ← assessment ID, scores, risk level, finding types, and recommendations only
```

The frontend is HTML/CSS/JavaScript. Flask hosts the static UI and JSON endpoints. SQLite stores derived outputs. The synthetic dashboard reads a reproducibly generated CSV and does not include live or visitor-level analytics.

## 10. Questionnaire Design

The 56 questions are divided into ten categories:

| Category | Questions | Weight |
|---|---:|---:|
| Profile visibility | 5 | 10% |
| Personal information | 7 | 15% |
| Location privacy | 6 | 15% |
| Posts and content | 6 | 10% |
| Friends and followers | 5 | 10% |
| Tagging and mentions | 4 | 5% |
| Authentication and account security | 8 | 15% |
| Third-party applications | 4 | 5% |
| Messaging and social engineering | 6 | 10% |
| Digital footprint | 5 | 5% |
| **Total** | **56** | **100%** |

Answers use closed enum sets such as YES/NO/SOMETIMES/NOT SURE, PUBLIC/FOLLOWERS-FRIENDS/PRIVATE, or NEVER/RARELY/SOMETIMES/OFTEN/NOT SURE. No free-text field is used. In the browser, not-yet-changed controls default to “Not sure”; this is a small review signal and the interface explains that users should verify settings directly.

## 11. Synthetic Dataset

The generator produces 1,200 fictional rows by default from a deterministic seed. IDs use the `SYN-` prefix. The requested CSV columns cover profile visibility, public exposure flags, selected controls, score, and risk level. Ten additional category columns support dashboard plots. The dataset contains no real names, handles, post text, email or phone values, precise location, or copied profile data.

## 12. Feature Engineering

`extract_privacy_features()` validates every question ID and response, then returns per-feature risk points and normalized ratios grouped into category totals. A public exposure answer receives a larger contribution; enabling a protective control reduces the account-security or privacy contribution. A “not sure” answer adds a smaller contribution so uncertainty prompts a review rather than being silently treated as safe.

## 13. Category Risk Analysis

The ten category scores range from 0 to 100, where 0 means lower assessed risk under this framework and 100 means higher. Categories separate information visibility from authentication, applications, social-engineering behavior, and historical content. A higher score does not mean an account has been compromised.

## 14. Risk Scoring

Each feature has a 0–4 educational risk scale. Per category, the highest feature ratio contributes 60% and the category mean contributes 40%. The category score is rounded to an integer. Overall risk is the weighted average using the weights in Section 10. Classification is LOW 0–20, MODERATE 21–40, HIGH 41–70, and CRITICAL 71–100.

The peak-aware blend is an explicit framework assumption designed so one severe answer is not hidden among several lower-risk answers. Weights and thresholds should be reviewed with domain experts, scenario testing, and an appropriately consented benchmark before use in a professional risk decision.

## 15. Findings Engine

A finding is produced when an answer has a non-zero contribution. Finding metadata provides a category, human-readable title, severity, priority, reason, and suggested action. Text is static metadata from the questionnaire, not copied from a profile or message. The top findings are ordered by priority and contribution severity.

## 16. Recommendation Engine

Recommendations are personalized to the non-zero findings and are deduplicated. Priority labels are IMMEDIATE, IMPORTANT, and GOOD PRACTICE. Typical actions include limiting phone visibility, disabling unnecessary real-time sharing, enabling tag approval and MFA, reviewing app permissions, and revisiting older posts.

## 17. Improvement Simulator

A user selects proposed changes. The API validates the original response map, checks each change against a server-side allow-list, copies the answers in memory, applies safer values, and runs the scoring engine again. It returns before/after scores and category values without storing the simulated input. It does not change settings on a social-media service and is clearly labelled as an educational model simulation.

## 18. Account Security and Third-Party Applications

The framework asks about MFA, password uniqueness, password reuse awareness, password-manager use, login alerts, recovery review, active sessions, unfamiliar devices, app review, unused integrations, permission scope, and social sign-in links. Passwords, recovery codes, app names, and device identifiers are never requested. Least privilege is expressed as granting an integration only the permissions needed for its purpose.

## 19. Location Privacy and Photo Awareness

Location questions cover current or real-time sharing, geotagging, check-ins, travel timing, vacation posts, and recurring patterns. Delayed posts can reduce immediate exposure compared with live broadcasting, though they do not remove every contextual clue. The release does not perform geolocation or analyze images. It explains EXIF metadata conceptually and recommends reviewing photo context and metadata locally before sharing.

## 20. Digital Footprint Analysis

The framework evaluates only whether the participant reviews old posts, unused accounts, old comments, profile history, and privacy settings. It does not search public websites, correlate handles, enumerate accounts, or build a profile of a person.

## 21. Dashboard and Report

The dashboard includes an overall synthetic mean, synthetic cohort risk distribution, category radar chart, most frequent synthetic weaknesses, and self-reported synthetic controls. The personal assessment results include an overall gauge, ten category bars/radar values, findings, prioritized actions, and the improvement comparison. The printable HTML report contains an assessment ID/date, scores, findings, recommendations, checklist, and disclaimer; it excludes raw questionnaire responses.

## 22. Privacy by Design

- **Data minimization:** Ask about visibility rather than collecting actual data values.
- **Purpose limitation:** Inputs support only the assessment and coaching response.
- **Least privilege:** No integration token or platform access exists.
- **Privacy by default:** No tracking, remote fonts, analytics, image uploads, or social login.
- **Transparency:** The scoring model and limitations are documented.
- **User control:** The person voluntarily runs, simulates, exports, or deletes a derived result.
- **Retention limitation:** Raw answers are not saved; derived data can be deleted.
- **Secure processing:** Strict allow-list validation, safe report escaping, request cap, parameterized SQL, and response headers.

## 23. Testing

The automated suite tests safe and fictional risky inputs; public contact, location, content, and workplace signals; unknown connections; tagging; MFA and alerts; password reuse awareness; app review; suspicious link behavior; historical content; feature extraction; weighted scores and exact band boundaries; recommendations; simulation; SQLite persistence; schema minimization; report generation and escaping; request validation; API creation/retrieval/deletion; security headers; questionnaire count; and synthetic demo labeling.

## 24. Security and Privacy Testing

The implementation has no columns for phone number, email, home address, birthday, password, exact location, or private message. The API rejects extra fields and answer strings outside the finite sets. Output is escaped in the report and rendered safely in the browser. API payloads are limited to 64 KiB, and a simple in-memory per-IP rate limit exists for the educational server. There are no user accounts or sessions; shared deployment would require additional controls.

## 25. Results

The deterministic fictional demo profile produces **57/100 — HIGH** with category scores: profile 68, personal information 71, location 80, content 0, connections 68, tagging 70, account security 70, third-party apps 70, social engineering 0, and digital footprint 68. Applying the full set of safer settings suggested by the demo findings simulates a change from 57 to 0 (57 points lower, LOW). This is a test fixture that demonstrates prioritization and the simulator; it is not a result about any real social-media account or a guarantee of safety.

## 26. Limitations

The answers are self-reported and cannot confirm real platform settings. Platform labels differ and may change. The model is not calibrated against incidents or expert judgments. The current version deliberately omits exported-profile parsing, scraping, account access, face detection, image upload, OCR, and EXIF extraction. The local Flask server has no authentication and is not intended for public hosting. Scores must not be used for hiring, admission, discipline, or high-impact decisions.

## 27. Future Scope

Safe extensions include platform-specific checklists, policy templates for voluntary workshops, awareness quizzes, maturity scoring, age-appropriate family safety modules, enterprise training without individual surveillance, GRC exports, anonymous opt-in aggregates, expert-reviewed calibration, accessible and localized interfaces, user-controlled trend comparison, and a local-only deployment option. Every extension should preserve consent, data minimization, transparent scoring, and deletion controls.

## 28. Conclusion

PRIVACY//FIELD demonstrates a practical, defensive privacy-risk workflow while minimizing data collection. Its strongest project contribution is not the numeric score by itself; it is the explainable process connecting a fixed-choice self-review to category-level risks, concrete recommendations, a transparent what-if simulation, privacy-preserving storage, and repeatable tests. It is an educational prototype that should be calibrated and governed before any professional deployment.
