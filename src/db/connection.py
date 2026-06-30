"""SQLite database connection utilities."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from src.config import DB_PATH, SCHEMA_PATH


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Create SQLite connection with row factory."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db_session(db_path: Path = DB_PATH):
    """Context manager for database sessions."""
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_schema(db_path: Path = DB_PATH, schema_path: Path = SCHEMA_PATH) -> None:
    """Apply schema SQL script."""
    with db_session(db_path) as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))


def run_query(query: str, params: tuple | None = None, db_path: Path = DB_PATH):
    """Execute a read query and return rows as dictionaries."""
    with db_session(db_path) as conn:
        cursor = conn.execute(query, params or ())
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
