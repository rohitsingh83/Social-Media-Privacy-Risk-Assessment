# Defensive Threat Model

## Scope and assumptions

This threat model discusses a **fictional social-media user** and the privacy coaching application. It is for awareness and defensive planning. It does not identify real people, enumerate accounts, or describe attack execution. The application does not access a real social-media account. Likelihood and impact are context-dependent educational judgments.

## Fictional user assets and threats

| Asset | Threat | Exposure / condition | Potential impact | Existing control | Recommended control |
|---|---|---|---|---|---|
| Account access | Account takeover | Reused password, MFA off, weak recovery hygiene, unreviewed sessions | Loss of account control; exposure of private content or contacts | Platform authentication controls; self-report assessment | Unique password, MFA, recovery review, sign-in alerts, session/device review |
| Identity information | Impersonation or unwanted correlation | Public profile fields, full birthday, repeated identity context | Confusion, reputational harm, unwanted account linkage | Audience settings and user awareness | Minimize public fields; review discoverability and audience settings |
| Contact information | Unwanted contact or social-engineering pressure | Personal phone/email visible publicly | Spam, harassment, convincing deceptive outreach | Platform profile controls | Hide unnecessary contact details; route contact through an intentional method |
| Location privacy | Unwanted location exposure | Live location, geotags, check-ins, travel timing, repetitive patterns | Unwanted attention, privacy loss, physical safety concern depending on context | Location and audience controls | Disable unneeded live sharing/geotagging; limit audience; consider delayed posts |
| Private content | Exposure after account compromise or oversharing | Account security gaps, automatic tag visibility, public posts | Loss of confidentiality or personal control | MFA, private audience, tag controls | Enable MFA, review active sessions, restrict and review tags/posts |
| Social relationships | Unwanted profiling or targeted pressure | Public friends/followers, tags, open connection requests | Relationship context becomes visible; unwanted contact | Follower-list and request controls | Restrict social graph; verify unknown requests; enable mention/tag review |
| Work / school context | Misuse of affiliation or access clues | Public workplace/education details or images showing badges/screens | More convincing impersonation; professional or physical-security concern | Awareness and content review | Limit details; crop/blur access clues; share with intended audience only |
| Family / children | Unintended exposure of another person's information | Public family imagery, names, school/routine context | Loss of consent/control; privacy or safety concern | Audience selection and consent practices | Consider the person's consent, reduce identifying context, narrow audience |
| Account-linked data | Third-party application exposure | Old integrations or broader-than-needed permissions | Data access beyond intended purpose | Platform's connected-app controls | Review integrations; revoke unused access; apply least privilege |

## Example privacy risk matrix

| Scenario | Likelihood | Impact | Context and defensive action |
|---|---|---|---|
| Public phone number | Medium | Medium | Exposure can invite unwanted contact or make a deceptive request more convincing. Hide it if public visibility is not necessary. |
| Real-time location sharing | Medium | High | Impact depends on audience and context. Limit live-sharing, geotags, or public check-ins; consider posting after leaving. |
| MFA disabled | Medium | High | This is an account-security concern rather than a public-data exposure by itself. Enable MFA and keep recovery options current. |
| Full birthday publicly visible | Medium | Medium | A birthday can contribute to unwanted correlation or social-engineering context. Limit visibility; do not assume it alone enables account access. |
| Old public posts not reviewed | Medium | Medium | Past audience and current intent can diverge. Revisit older content and current platform controls. |
| Unused third-party access | Low–Medium | Medium | Impact depends on granted permissions and service. Review actual platform settings and revoke access no longer needed. |

Likelihood and impact may differ significantly by platform, threat environment, personal circumstances, and audience. The matrix is not a universal prediction.

## Application-level risks and controls

| Application concern | Defensive control in this prototype | Remaining limitation / next step |
|---|---|---|
| Accidental PII collection | Fixed-choice questions; no free-text field; unknown fields rejected | Review UI and API whenever new questions are added. |
| Raw answer retention | Database schema has no answer/payload column | Server memory/logging/deployment behavior still matters; avoid request-body logging in future hosting. |
| Injection / XSS | Enum validation, static recommendation text, HTML escaping, restrictive CSP | Continue dependency updates and add dedicated browser security tests. |
| Oversized requests | 64 KiB cap | Tune limits if contract changes; never accept arbitrary file uploads by default. |
| Brute-force API requests | Simple in-memory per-IP throttling | Not distributed, persistent, or production-grade. Replace with a vetted limiter behind a proxy. |
| Unauthorized read/delete | Local single-user prototype; opaque random assessment ID | IDs are not authorization. Add authentication, ownership checks, CSRF protection, and access auditing before shared use. |
| Database disclosure | Store only derived values; local SQLite ignored by Git | Protect file permissions, backups, retention, host and encryption requirements in a real deployment. |
| Insecure report | Escaped static output; no raw answer fields; same-origin script | Re-test escaping if new user-controlled fields are added. |
| Misleading decisions | Educational disclaimer, transparent weights, no identity/profile data | Prohibit high-impact decisions; perform calibration, bias review, governance, and human review before any broader use. |
| Accidental tracking | No third-party analytics, remote fonts, scraping, or account API | Review future dependencies and network calls; maintain a data-flow inventory. |

## Trust boundaries

1. **Browser → Flask API:** JSON contains only fixed-choice questionnaire values and approved simulator IDs. Validate every request; do not log body contents.
2. **Flask → scoring modules:** responses are transient; modules must not write raw answers to disk or emit them in exceptions.
3. **Flask → SQLite:** parameterized statements store derived outputs only. Foreign keys support deletion.
4. **Synthetic CSV → dashboard:** the aggregate pipeline reads generated fictional rows; it must not be replaced with user or scraped data without consent, privacy review, and a separate design.
5. **Report → browser print:** report fields are escaped and the document contains only derived data.

## Ethical use

Use only for self-assessment or explicitly authorized, voluntary education. Do not assess someone else without consent. Do not use results for hiring, admissions, discipline, insurance, eligibility, or covert monitoring. The score must not be treated as proof of unsafe behavior or of an account compromise.
