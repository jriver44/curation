from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from uuid import UUID

from domain import Collection, Item
from storage.base import Storage

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


def _norm(s: str) -> str:
    return s.strip().casefold()


def _clean_display(s: str) -> str:
    return s.strip()


def _parse_datetime(raw: str) -> datetime:
    s = raw.strip()
    if s.endswith("Z"):
        s = s[:-1]
    return datetime.fromisoformat(s)


class SQLiteStorage(Storage):
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    def list_collections(self) -> Iterable[str]:
        conn = connect(self._database_path)

        try:
            init_database(conn)
            rows = conn.execute("SELECT name FROM collections ORDER BY name;").fetchall()
            return [str(row["name"]) for row in rows]
        finally:
            conn.close()

    def load_collection(self, name: str) -> Collection:
        name_norm = _norm(name)
        display_name = _clean_display(name)
        
        conn = connect(self._database_path)
        
        try:
            init_database(conn)
            
            collection_row = conn.execute(
                "SELECT id, name FROM collections WHERE name_norm = ?;",
                (name_norm,),
            ).fetchone()
        
            if collection_row is None:
                return Collection(name=display_name, items=[])
        
            collection_id = int(collection_row["id"])
            collection_name = str(collection_row["name"])
        
            item_rows = conn.execute(
                """
                SELECT id, name, category, quantity, created_at, updated_at
                FROM items
                WHERE collection_id = ?
                ORDER BY category_norm, name_norm;
                """,
                (collection_id,),
            ).fetchall()
        
            items: list[Item] = []
        
            for row in item_rows:
                created_at = _parse_datetime(str(row["created_at"]))
                updated_raw = row["updated_at"]
                updated_at = _parse_datetime(str(updated_raw)) if updated_raw is not None else None
            
                items.append(
                    Item(
                        id=UUID(str(row["id"])),
                        name=str(row["name"]),
                        category=str(row["category"]),
                        quantity=int(row["quantity"]),
                        created_at=created_at,
                        updated_at=updated_at,
                    )
                )
            return Collection(name=collection_name, items=items)
        finally:
            conn.close()
        
        

    def save_collection(self, collection: Collection) -> None:
        raise NotImplementedError
