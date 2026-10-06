"""SQLite persistence for derived, non-identifying assessment outputs only."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(db_path: str | Path) -> None:
    with connect(db_path) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS assessments (
                assessment_id TEXT PRIMARY KEY,
                overall_score INTEGER NOT NULL CHECK (overall_score BETWEEN 0 AND 100),
                risk_level TEXT NOT NULL CHECK (risk_level IN ('LOW','MODERATE','HIGH','CRITICAL')),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS category_scores (
                category_score_id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id TEXT NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
                category TEXT NOT NULL,
                score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
                weight INTEGER NOT NULL CHECK (weight >= 0),
                UNIQUE (assessment_id, category)
            );
            CREATE TABLE IF NOT EXISTS findings (
                finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id TEXT NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
                category TEXT NOT NULL,
                finding_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id TEXT NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
                finding_type TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                priority TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_findings_assessment ON findings(assessment_id);
            CREATE INDEX IF NOT EXISTS idx_recommendations_assessment ON recommendations(assessment_id);
        """)


def save_assessment(db_path: str | Path, assessment_id: str, result: dict[str, Any]) -> None:
    """Persist only score bands, category totals, finding types and coaching."""
    with connect(db_path) as db:
        db.execute(
            "INSERT INTO assessments (assessment_id, overall_score, risk_level, created_at) VALUES (?, ?, ?, ?)",
            (assessment_id, result["overall_score"], result["risk_level"], result["assessed_at"]),
        )
        db.executemany(
            "INSERT INTO category_scores (assessment_id, category, score, weight) VALUES (?, ?, ?, ?)",
            [
                (assessment_id, key, value["score"], value["weight"])
                for key, value in result["category_scores"].items()
            ],
        )
        db.executemany(
            "INSERT INTO findings (assessment_id, category, finding_type, severity, description) VALUES (?, ?, ?, ?, ?)",
            [
                (assessment_id, finding["category"], finding["finding_type"], finding["severity"], finding["title"])
                for finding in result["findings"]
            ],
        )
        db.executemany(
            "INSERT INTO recommendations (assessment_id, finding_type, recommendation, priority) VALUES (?, ?, ?, ?)",
            [
                (assessment_id, item["finding_type"], item["recommendation"], item["priority"])
                for item in result["recommendations"]
            ],
        )


def get_assessment(db_path: str | Path, assessment_id: str) -> dict[str, Any] | None:
    with connect(db_path) as db:
        row = db.execute(
            "SELECT assessment_id, overall_score, risk_level, created_at FROM assessments WHERE assessment_id = ?",
            (assessment_id,),
        ).fetchone()
        if row is None:
            return None
        categories = db.execute(
            "SELECT category, score, weight FROM category_scores WHERE assessment_id = ? ORDER BY category_score_id",
            (assessment_id,),
        ).fetchall()
        findings = db.execute(
            "SELECT category, finding_type, severity, description FROM findings WHERE assessment_id = ? ORDER BY finding_id",
            (assessment_id,),
        ).fetchall()
        recommendations = db.execute(
            "SELECT finding_type, recommendation, priority FROM recommendations WHERE assessment_id = ? ORDER BY recommendation_id",
            (assessment_id,),
        ).fetchall()
    from backend.services.questionnaire import CATEGORY_MAP, QUESTION_MAP
    category_scores = {
        item["category"]: {
            "label": CATEGORY_MAP[item["category"]]["label"],
            "short": CATEGORY_MAP[item["category"]]["short"],
            "score": item["score"],
            "weight": item["weight"],
        }
        for item in categories
    }
    finding_list = []
    for item in findings:
        question = QUESTION_MAP.get(item["finding_type"], {})
        finding_list.append({
            "category": item["category"],
            "category_label": CATEGORY_MAP[item["category"]]["label"],
            "finding_type": item["finding_type"],
            "severity": item["severity"],
            "title": item["description"],
            "description": question.get("help", "Review this setting."),
            "priority": question.get("priority", "IMPORTANT"),
            "recommendation": question.get("recommendation", "Review the associated privacy setting."),
        })
    recommendation_list = []
    for item in recommendations:
        question = QUESTION_MAP.get(item["finding_type"], {})
        recommendation_list.append({
            "finding_type": item["finding_type"],
            "category": question.get("category", "profile"),
            "category_label": CATEGORY_MAP.get(question.get("category", "profile"), {}).get("label", "Profile"),
            "risk": question.get("finding_title", "Privacy setting to review"),
            "recommendation": item["recommendation"],
            "priority": item["priority"],
        })
    return {
        "assessment_id": row["assessment_id"],
        "overall_score": row["overall_score"],
        "risk_level": row["risk_level"],
        "created_at": row["created_at"],
        "category_scores": category_scores,
        "findings": finding_list,
        "recommendations": recommendation_list,
        "finding_count": len(finding_list),
        "recommendation_count": len(recommendation_list),
    }


def delete_assessment(db_path: str | Path, assessment_id: str) -> bool:
    with connect(db_path) as db:
        cursor = db.execute("DELETE FROM assessments WHERE assessment_id = ?", (assessment_id,))
        return cursor.rowcount > 0


def dashboard_persistence_stats(db_path: str | Path) -> dict[str, int | float]:
    with connect(db_path) as db:
        row = db.execute("SELECT COUNT(*) AS total, COALESCE(AVG(overall_score), 0) AS average FROM assessments").fetchone()
    return {"stored_assessments": int(row["total"]), "stored_average_score": round(float(row["average"]), 1)}
