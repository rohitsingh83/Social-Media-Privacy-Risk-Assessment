"""REST API blueprint. Every assessment payload is enum-only and transient."""
from __future__ import annotations

import re
import uuid
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from backend.models.database import (
    dashboard_persistence_stats,
    delete_assessment,
    get_assessment,
    save_assessment,
)
from backend.services.assessment_engine import analyze_responses
from backend.services.dashboard_analytics import load_synthetic_dashboard
from backend.services.improvement_simulator import simulate_improvements
from backend.services.questionnaire import action_catalog, public_questionnaire, safe_demo_responses
from backend.services.reporting import build_report_html, checklist_payload

api_bp = Blueprint("api", __name__, url_prefix="/api")
ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "data" / "social_media_privacy_assessments.csv"
ASSESSMENT_ID_RE = re.compile(r"^[0-9a-f]{32}$")


@api_bp.get("/health")
def health():
    return jsonify({"status": "ok", "mode": "local educational assessment", "raw_responses_persisted": False})


@api_bp.get("/questionnaire")
def questionnaire():
    groups = public_questionnaire()
    return jsonify({"groups": groups, "question_count": sum(len(group["questions"]) for group in groups)})


@api_bp.get("/improvements")
def improvements():
    return jsonify({"actions": action_catalog(), "simulation_only": True})


@api_bp.get("/demo-profile")
def demo_profile():
    return jsonify({"fictional": True, "responses": safe_demo_responses(), "notice": "Synthetic classroom demo only."})


@api_bp.post("/assessment")
def create_assessment():
    if not request.is_json:
        return jsonify({"error": "Send a JSON request."}), 415
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or set(payload) != {"responses"}:
        return jsonify({"error": "Request must contain only a responses object."}), 400
    try:
        result = analyze_responses(payload["responses"])
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    assessment_id = uuid.uuid4().hex
    save_assessment(current_app.config["DATABASE_PATH"], assessment_id, result)
    response = dict(result)
    response["assessment_id"] = assessment_id
    response["storage_notice"] = "Only derived scores, finding types, and recommendations were stored; questionnaire answers were not stored."
    return jsonify(response), 201


@api_bp.get("/assessment/<assessment_id>")
def read_assessment(assessment_id: str):
    if not ASSESSMENT_ID_RE.fullmatch(assessment_id):
        return jsonify({"error": "Assessment not found."}), 404
    result = get_assessment(current_app.config["DATABASE_PATH"], assessment_id)
    if result is None:
        return jsonify({"error": "Assessment not found."}), 404
    return jsonify(result)


@api_bp.get("/assessment/<assessment_id>/recommendations")
def read_recommendations(assessment_id: str):
    if not ASSESSMENT_ID_RE.fullmatch(assessment_id):
        return jsonify({"error": "Assessment not found."}), 404
    result = get_assessment(current_app.config["DATABASE_PATH"], assessment_id)
    if result is None:
        return jsonify({"error": "Assessment not found."}), 404
    return jsonify({"assessment_id": assessment_id, "recommendations": result["recommendations"]})


@api_bp.delete("/assessment/<assessment_id>")
def remove_assessment(assessment_id: str):
    if not ASSESSMENT_ID_RE.fullmatch(assessment_id):
        return jsonify({"error": "Assessment not found."}), 404
    removed = delete_assessment(current_app.config["DATABASE_PATH"], assessment_id)
    if not removed:
        return jsonify({"error": "Assessment not found."}), 404
    return jsonify({"deleted": True, "assessment_id": assessment_id})


@api_bp.get("/assessment/<assessment_id>/report")
def assessment_report(assessment_id: str):
    if not ASSESSMENT_ID_RE.fullmatch(assessment_id):
        return jsonify({"error": "Assessment not found."}), 404
    result = get_assessment(current_app.config["DATABASE_PATH"], assessment_id)
    if result is None:
        return jsonify({"error": "Assessment not found."}), 404
    html = build_report_html(result)
    return current_app.response_class(html, mimetype="text/html")


@api_bp.post("/assessment/simulate-improvement")
def simulate():
    if not request.is_json:
        return jsonify({"error": "Send a JSON request."}), 415
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or set(payload) != {"responses", "changes"}:
        return jsonify({"error": "Request must contain responses and changes only."}), 400
    try:
        result = simulate_improvements(payload["responses"], payload["changes"])
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(result)


@api_bp.get("/dashboard/stats")
def dashboard_stats():
    if not DATASET_PATH.exists():
        return jsonify({"error": "Synthetic demo dataset is missing. Run the dataset generator."}), 503
    stats = load_synthetic_dashboard(DATASET_PATH)
    stats.update(dashboard_persistence_stats(current_app.config["DATABASE_PATH"]))
    stats["model_note"] = "Cohort figures come from fictional records, not live social accounts."
    return jsonify(stats)


@api_bp.get("/privacy-checklist")
def privacy_checklist():
    return jsonify({"checklist": checklist_payload()})
