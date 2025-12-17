import sqlite3
from pathlib import Path

from storage.sqlite_storage import connect, init_database


def table_names(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    return {r[0] for r in rows}


def test_init_database_create_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "test.db"
    conn = connect(database_path)

    try:
        init_database(conn)
        names = table_names(conn)
        assert "collections" in names
        assert "items" in names
    finally:
        conn.close()


def test_foreign_keys_enforced(tmp_path: Path) -> None:
    database_path = tmp_path / "test.db"
    conn = connect(database_path)

    try:
        init_database(conn)
        f_key = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        assert f_key == 1
    finally:
        conn.close()


def test_quantity_constraint(tmp_path: Path) -> None:
    database_path = tmp_path / "test.db"
    conn = connect(database_path)

    try:
        init_database(conn)

        conn.execute(
            "INSERT INTO collections (name, name_norm, created_at) VALUES (?, ?, ?)",
            ("Test", "test", "2025-01-01T00:00:00Z"),
        )

        conn_id = conn.execute(
            "SELECT id FROM collections WHERE name_norm = ?",
            ("test",),
        ).fetchone()[0]

        # quantity must be > 0
        try:
            conn.execute(
                """
                INSERT INTO items (id, collection_id, name, name_norm, category, category_norm,
                                    quantity, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "uuid-1",
                    conn_id,
                    "Thing",
                    "thing",
                    "Cat",
                    "cat",
                    0,
                    "2025-01-01T00:00:00Z",
                    None,
                ),
            )
            conn.commit()
            raise AssertionError("Expected CHECK constraint failure for quantity")
        except sqlite3.IntegrityError:
            pass
    finally:
        conn.close()


def test_unique_logical_item_per_collection(tmp_path: Path) -> None:
    database_path = tmp_path / "test.db"

    conn = connect(database_path)

    try:
        init_database(conn)

        conn.execute(
            """
            INSERT INTO collections (name, name_norm, created_at) 
            VALUES (?, ?, ?)
            """,
            ("Test", "test", "2025-01-01T00:00:00Z"),
        )

        conn_id = conn.execute(
            """
            SELECT id FROM collections WHERE name_norm = ?
            """,
            ("test",),
        ).fetchone()[0]

        conn.execute(
            """
            INSERT INTO items (id, collection_id, name, name_norm, category, category_norm,
                                quantity, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "uuid-1",
                conn_id,
                "Padron X000",
                "padron x000",
                "Cigar",
                "cigar",
                1,
                "2025-01-01T00:00:00Z",
                None,
            ),
        )

        conn.commit()

        # Same logical item (same norms) should violabe UNIQUE
        try:
            conn.execute(
                """
                INSERT INTO items (id, collection_id, name, name_norm, category, category_norm,
                                quantity, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "uuid-2",
                    conn_id,
                    "padron x000",
                    "padron x000",
                    "cigar",
                    "cigar",
                    1,
                    "2025-01-01T00:00:00Z",
                    None,
                ),
            )

            conn.commit()
            raise AssertionError(
                "Expected UNIQUE constraint failure for (collection_id, name_norm, category_norm)"
            )
        except sqlite3.IntegrityError:
            pass
    finally:
        conn.close()
