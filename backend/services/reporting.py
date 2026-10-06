"""Self-contained, printable HTML report and privacy checklist."""
from __future__ import annotations

from html import escape

CHECKLIST = [
    "Review profile visibility and public search discoverability.",
    "Hide unnecessary contact information and full birth-date visibility.",
    "Review workplace, education, family, and relationship details.",
    "Review location sharing, geotags, check-ins, and routine patterns.",
    "Avoid unnecessary real-time location and travel announcements.",
    "Review who can see posts, followers, and connection lists.",
    "Restrict tagging and enable approval before tags appear.",
    "Verify unfamiliar connection requests before accepting them.",
    "Enable multi-factor authentication using a strong supported method.",
    "Use unique passwords; consider a reputable password manager.",
    "Enable login alerts and review recovery options.",
    "Review active sessions and unfamiliar devices in platform settings.",
    "Review connected third-party apps and remove unused integrations.",
    "Apply least privilege to permissions granted to connected apps.",
    "Review photo framing and metadata before sharing.",
    "Pause before opening unexpected links or acting on urgent messages.",
    "Never share one-time verification codes or recovery codes.",
    "Review older public posts, comments, profile history, and unused accounts.",
    "Schedule a privacy-settings review every few months.",
]


def checklist_payload() -> list[dict]:
    return [{"id": f"check-{index + 1}", "text": item} for index, item in enumerate(CHECKLIST)]


def build_report_html(assessment: dict) -> str:
    """Render a safe print view containing only derived assessment data."""
    assessment_id = escape(str(assessment.get("assessment_id", "local")))
    created_at = escape(str(assessment.get("created_at", assessment.get("assessed_at", ""))))
    score = int(assessment.get("overall_score", 0))
    level = escape(str(assessment.get("risk_level", "LOW")))
    categories = assessment.get("category_scores", {})
    if isinstance(categories, list):
        category_items = categories
    else:
        category_items = [
            {"label": meta.get("label", key), "score": meta.get("score", 0), "weight": meta.get("weight", 0)}
            for key, meta in categories.items()
        ]
    category_rows = "".join(
        "<tr><td>{}</td><td>{}/100</td><td>{}%</td></tr>".format(
            escape(str(item.get("label", "Category"))),
            int(item.get("score", 0)),
            int(item.get("weight", 0)),
        ) for item in category_items
    )
    findings = assessment.get("findings", [])[:12]
    findings_html = "".join(
        "<li><strong>{}</strong> <span class='tag'>{}</span><br><span>{}</span></li>".format(
            escape(str(item.get("title", "Privacy finding"))),
            escape(str(item.get("priority", item.get("severity", "REVIEW")))),
            escape(str(item.get("recommendation", item.get("description", "Review this setting.")))),
        ) for item in findings
    ) or "<li>No elevated findings were identified by this educational model.</li>"
    recs = assessment.get("recommendations", [])[:12]
    recs_html = "".join(
        "<li><span class='tag'>{}</span> {}</li>".format(
            escape(str(item.get("priority", "REVIEW"))),
            escape(str(item.get("recommendation", "Review the associated setting."))),
        ) for item in recs
    ) or "<li>Maintain current privacy practices and review settings periodically.</li>"
    checks = "".join(f"<li>□ {escape(item)}</li>" for item in CHECKLIST)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Privacy Assessment Report — {assessment_id}</title>
<style>
:root{{--ink:#152329;--muted:#64777d;--line:#d9e3e1;--mint:#0e8a72;--paper:#f5f7f4}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:900px;margin:32px auto;padding:48px;background:#fff;border:1px solid var(--line);border-radius:20px}}
header{{display:flex;justify-content:space-between;gap:24px;align-items:flex-start;border-bottom:1px solid var(--line);padding-bottom:24px}}
.eyebrow{{font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--mint);font-weight:800}}
h1{{font-size:32px;line-height:1.08;margin:8px 0}}h2{{font-size:18px;margin:28px 0 10px}}
.meta,.muted{{color:var(--muted);font-size:13px}}.score{{font-size:40px;font-weight:850;white-space:nowrap;color:var(--mint)}}
.score small{{font-size:14px;color:var(--muted)}}table{{width:100%;border-collapse:collapse}}td,th{{text-align:left;padding:10px;border-bottom:1px solid var(--line)}}th{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em}}
li{{padding:6px 0}}.tag{{display:inline-block;background:#e8f7f1;color:#176c5d;border-radius:20px;padding:2px 9px;font-size:10px;font-weight:800;text-transform:uppercase;margin:0 5px}}
.notice{{margin-top:26px;background:#f1f5f2;padding:16px;border-radius:12px;color:#516267;font-size:12px}}
button{{position:fixed;top:18px;right:18px;background:#10262a;color:white;border:0;border-radius:999px;padding:12px 18px;font-weight:700;cursor:pointer}}
@media print{{body{{background:#fff}}main{{margin:0 auto;padding:20px;border:0}}button{{display:none}}}}
@media(max-width:640px){{main{{margin:12px;padding:22px}}header{{display:block}}.score{{margin-top:14px}}}}
</style><script src="/assets/report.js" defer></script></head><body><button id="print-button" type="button">Print / Save as PDF</button><main>
<header><div><div class="eyebrow">Privacy Field Notes · Educational assessment</div><h1>Social media privacy report</h1>
<div class="meta">Assessment ID: {assessment_id}<br>Assessment date: {created_at}</div></div>
<div class="score">{score}<small> / 100<br>{level}</small></div></header>
<h2>Category risk scores</h2><table><thead><tr><th>Category</th><th>Risk</th><th>Weight</th></tr></thead><tbody>{category_rows}</tbody></table>
<h2>Top findings and actions</h2><ol>{findings_html}</ol><h2>Recommendations</h2><ol>{recs_html}</ol>
<h2>Privacy checklist</h2><ul class="checklist">{checks}</ul>
<div class="notice"><strong>Interpretation:</strong> A higher score means more risk according to this educational framework. The questionnaire collects settings/practice choices only. This report does not contain profile text, contact details, passwords, precise locations, photos, private messages, or social-media identifiers. The score is not a guarantee or prediction that an account will or will not be compromised. Validate the weights and thresholds before any professional decision.</div>
</main></body></html>"""
