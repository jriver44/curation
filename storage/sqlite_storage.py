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
        conn = connect(self._database_path)
        try:
            init_database(conn)

            collection_display = _clean_display(collection.name)
            collection_normal = _norm(collection.name)
            now = datetime.utcnow().isoformat()

            with conn:
                # all or nothing save
                # upsert collection using logical key by name_norm
                conn.execute(
                    """
                             INSERT INTO collections (name, name_norm, created_at)
                             VALUES (?, ?, ?)
                             ON CONFLICT(name_norm) DO UPDATE SET
                                name = excluded.name;
                             """,
                    (collection_display, collection_normal, now),
                )

                row = conn.execute(
                    "SELECT id FROM collections WHERE name_norm = ?;",
                    (collection_normal,),
                ).fetchone()

                if row is None:
                    raise RuntimeError("Failed to fetch collection id after upsert.")
                collection_id = int(row["id"])

                # upsert items using a logical key (collection_id, name_norm, category_norm)
                for item in collection.items:
                    name_display = _clean_display(item.name)
                    category_display = _clean_display(item.category)
                    name_norm = _norm(item.name)
                    category_norm = _norm(item.category)

                    conn.execute(
                        """
                        INSERT INTO items (
                            id, collection_id,
                            name, name_norm,
                            category, category_norm,
                            quantity, created_at, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(collection_id, name_norm, category_norm) DO UPDATE SET
                            name = excluded.name,
                            category = excluded.category,
                            quantity = excluded.quantity,
                            updated_at = ?;
                        """,
                        (
                            str(item.id),
                            collection_id,
                            name_display,
                            name_norm,
                            category_display,
                            category_norm,
                            int(item.quantity),
                            item.created_at.isoformat(),
                            item.updated_at.isoformat() if item.updated_at else None,
                            now,
                        ),
                    )

                # delete database rows that are no longer in memory
                pairs = [(_norm(i.name), _norm(i.category)) for i in collection.items]

                if not pairs:
                    conn.execute(
                        "DELETE FROM items WHERE collection_id = ?;",
                        (collection_id,),
                    )
                else:
                    placeholders = ",".join(["(?, ?)"] * len(pairs))
                    parameters: list[object] = [collection_id]

                    for nam_nor, cat_nor in pairs:
                        parameters.extend([nam_nor, cat_nor])

                    conn.execute(
                        f"""
                        DELETE FROM items
                        WHERE collection_id = ?
                            AND (name_norm, category_norm) NOT IN ({placeholders});
                        """,
                        parameters,
                    )
        finally:
            conn.close()
