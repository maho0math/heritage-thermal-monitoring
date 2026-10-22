"""Схема общей базы данных платформы мониторинга."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "heritage_thermal.sqlite3"


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS heritage_objects (
    id                TEXT PRIMARY KEY,
    title             TEXT NOT NULL,
    address           TEXT NOT NULL,
    year_built        INTEGER NOT NULL CHECK (year_built > 1000),
    style             TEXT NOT NULL,
    wall_material     TEXT NOT NULL,
    protection_status TEXT NOT NULL,
    source            TEXT NOT NULL DEFAULT 'heritage_store'
);

CREATE TABLE IF NOT EXISTS tags (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS object_tags (
    object_id TEXT NOT NULL,
    tag_id    INTEGER NOT NULL,
    PRIMARY KEY (object_id, tag_id),
    FOREIGN KEY (object_id) REFERENCES heritage_objects(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id)    REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS thermal_readings (
    id          TEXT PRIMARY KEY,
    object_id   TEXT NOT NULL,
    temperature REAL NOT NULL,
    humidity    REAL NOT NULL CHECK (humidity >= 0 AND humidity <= 100),
    timestamp   TEXT NOT NULL,
    source      TEXT NOT NULL DEFAULT 'thermal_store',
    FOREIGN KEY (object_id) REFERENCES heritage_objects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_readings_object ON thermal_readings(object_id);
CREATE INDEX IF NOT EXISTS idx_readings_ts     ON thermal_readings(timestamp);
"""


def get_connection(db_path=None):
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn=None):
    own = conn is None
    if own:
        conn = get_connection()
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        if own:
            conn.close()


if __name__ == "__main__":
    create_schema()
    print(f"Схема создана: {DB_PATH}")