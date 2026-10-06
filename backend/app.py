"""Flask application entry point for the local privacy assessment demo."""
from __future__ import annotations

import os
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory

from backend.models.database import initialize_database
from backend.routes.api import api_bp

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"
_RATE_STATE: dict[str, list[float]] = {}
_RATE_LOCK = threading.Lock()
RATE_LIMIT = 120
RATE_WINDOW_SECONDS = 60


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, static_folder=None)
    default_db = ROOT / "instance" / "privacy_assessments.sqlite3"
    app.config.update(
        DATABASE_PATH=os.environ.get("DATABASE_PATH", str(default_db)),
        MAX_CONTENT_LENGTH=64 * 1024,
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)
    initialize_database(app.config["DATABASE_PATH"])

    @app.before_request
    def apply_api_rate_limit():
        if not request.path.startswith("/api/"):
            return None
        now = time.monotonic()
        client_key = request.remote_addr or "local"
        with _RATE_LOCK:
            timestamps = [stamp for stamp in _RATE_STATE.get(client_key, []) if now - stamp < RATE_WINDOW_SECONDS]
            if len(timestamps) >= RATE_LIMIT:
                _RATE_STATE[client_key] = timestamps
                return jsonify({"error": "Too many requests. Please pause and try again shortly."}), 429
            timestamps.append(now)
            _RATE_STATE[client_key] = timestamps
        return None

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        )
        response.headers["Cache-Control"] = "no-store" if request.path.startswith("/api/") else "no-cache"
        return response

    @app.errorhandler(413)
    def payload_too_large(_error):
        return jsonify({"error": "Request is too large. Only the small questionnaire payload is accepted."}), 413

    @app.get("/")
    def home():
        return send_file(FRONTEND_DIR / "index.html")

    @app.get("/assets/<path:asset_path>")
    def assets(asset_path: str):
        return send_from_directory(FRONTEND_DIR / "assets", asset_path, max_age=0)

    app.register_blueprint(api_bp)
    return app


app = create_app()

if __name__ == "__main__":
    # A local learning/demo server only. Add authentication, HTTPS, and a
    # production WSGI server before any shared or public deployment.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), debug=False, use_reloader=False)
