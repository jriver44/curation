from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS collections(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    name_norm   TEXT NOT NULL UNIQUE,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS items(
    id              TEXT PRIMARY KEY,
    collection_id   INTEGER NOT NULL,
    name            TEXT NOT NULL,
    name_norm       TEXT NOT NULL,
    category        TEXT NOT NULL,
    category_norm   TEXT NOT NULL,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    created_at      TEXT NOT NULL,
    updated_at      TEXT,
    
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
    UNIQUE (collection_id, name_norm, category_norm)
);

CREATE INDEX IF NOT EXISTS id_items_collection ON items(collection_id);
CREATE INDEX IF NOT EXISTS idx_items_search ON items (collection_id, name_norm);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(collection_id, category_norm);
"""

def connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    
    # FK enforcement always enabled for connection
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_database(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()