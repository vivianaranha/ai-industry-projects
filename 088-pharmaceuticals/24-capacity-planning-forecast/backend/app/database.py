"""Tiny SQLite persistence layer used by the API.

SQLite keeps the project beginner-friendly while still demonstrating an
important production concept: requests/results should be persisted so they can
be audited, analyzed, and used for future model improvement.
"""
from pathlib import Path
import json
import sqlite3
from datetime import datetime, timezone
from .config import settings


def _connect() -> sqlite3.Connection:
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    with _connect() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS inference_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                input_json TEXT NOT NULL,
                output_json TEXT NOT NULL
            )"""
        )
        conn.commit()


def save_inference(input_payload: dict, output_payload: dict) -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO inference_history(created_at,input_json,output_json) VALUES(?,?,?)",
            (
                datetime.now(timezone.utc).isoformat(),
                json.dumps(input_payload),
                json.dumps(output_payload),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_history(limit: int = 50) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM inference_history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [
        {
            "id": row["id"],
            "created_at": row["created_at"],
            "input": json.loads(row["input_json"]),
            "output": json.loads(row["output_json"]),
        }
        for row in rows
    ]
