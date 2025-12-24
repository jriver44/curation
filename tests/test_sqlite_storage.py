from datetime import datetime
from pathlib import Path
from uuid import uuid4

from domain import Collection, Item
from storage.sqlite_storage import SQLiteStorage, connect, init_database


def test_list_collections_empty(tmp_path: Path) -> None:
    database = tmp_path / "curation.db"
    storage = SQLiteStorage(database)

    assert storage.list_collections() == []


def test_list_collections_returns_sorted_names(tmp_path: Path):
    database = tmp_path / "curation.db"

    conn = connect(database)

    try:
        init_database(conn)
        now = datetime.utcnow().isoformat()

        conn.execute(
            "INSERT INTO collections (name, name_norm, created_at) VALUES (?, ?, ?);",
            ("Zed", "Zed", now),
        )

        conn.execute(
            "INSERT INTO collections (name, name_norm, created_at) VALUES (?, ?, ?);",
            ("Alpha", "alpha", now),
        )

        conn.commit()
    finally:
        conn.close()

    storage = SQLiteStorage(database)
    assert storage.list_collections() == ["Alpha", "Zed"]


def test_load_missing_collection_returns_empty(tmp_path: Path) -> None:
    database = tmp_path / "curation.db"
    storage = SQLiteStorage(database)

    collection = storage.load_collection("Does Not Exist")

    assert collection.name == "Does Not Exist"
    assert collection.items == []


def test_load_collection_returns_items(tmp_path: Path) -> None:
    database = tmp_path / "curation.db"
    now = datetime.utcnow().isoformat()

    conn = connect(database)
    try:
        init_database(conn)

        conn.execute(
            "INSERT INTO collections (name, name_norm, created_at) VALUES (?, ?, ?);",
            ("Cigars", "cigars", now),
        )

        collection_id = conn.execute(
            "SELECT id FROM collections WHERE name_norm = ?;",
            ("cigars",),
        ).fetchone()["id"]

        item_id = str(uuid4())

        conn.execute(
            """
            INSERT INTO items (
                id, collection_id,
                name, name_norm,
                category, category_norm,
                quantity, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                item_id,
                collection_id,
                "Padron 1964",
                "padron 1964",
                "Cigar",
                "cigar",
                2,
                now,
                None,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    storage = SQLiteStorage(database)
    loaded = storage.load_collection("  CIGARS  ")

    assert loaded.name == "Cigars"
    assert len(loaded.items) == 1
    assert loaded.items[0].name == "Padron 1964"
    assert loaded.items[0].category == "Cigar"
    assert loaded.items[0].quantity == 2


def test_save_then_load_roundtrip(tmp_path: Path) -> None:
    database = tmp_path / "curation.db"
    storage = SQLiteStorage(database)

    collection = Collection(
        name="Cigars",
        items=[
            Item(id=uuid4(), name="Padron 1964", category="Cigar", quantity=2),
            Item(id=uuid4(), name="Trinidad", category="Cigar", quantity=1),
        ],
    )

    storage.save_collection(collection)
    loaded = storage.load_collection("  CIGARS  ")

    assert loaded.name == "Cigars"
    assert len(loaded.items) == 2
    assert sorted((i.name, i.quantity) for i in loaded.items) == [
        ("Padron 1964", 2),
        ("Trinidad", 1),
    ]


def test_save_updates_quantity_without_duplication(tmp_path: Path) -> None:
    database = tmp_path / "curation.db"
    storage = SQLiteStorage(database)

    item = Item(id=uuid4(), name="Padron 1964", category="Cigar", quantity=2)
    collection = Collection(name="Cigars", items=[item])

    storage.save_collection(collection)

    loaded = storage.load_collection("cigars")

    assert loaded.name == "Cigars"
    assert len(loaded.items) == 1
    assert loaded.items[0].name == "Padron 1964"
    assert loaded.items[0].category == "Cigar"
    assert loaded.items[0].quantity == 2


def test_save_deletes_removed_items(tmp_path: Path) -> None:
    database = tmp_path / "curation.db"
    storage = SQLiteStorage(database)

    item_a = Item(id=uuid4(), name="Padron 1964", category="Cigar", quantity=2)
    item_b = Item(id=uuid4(), name="Trinidad", category="Cigar", quantity=1)
    collection = Collection(name="Cigars", items=[item_a, item_b])

    storage.save_collection(collection)

    collection.items = [item_a]
    storage.save_collection(collection)

    loaded = storage.load_collection("cigars")
    assert sorted(i.name for i in loaded.items) == ["Padron 1964"]


def test_save_empty_collection_deletes_all_items(tmp_path: Path) -> None:
    database = tmp_path / "curation.db"
    storage = SQLiteStorage(database)

    item_a = Item(id=uuid4(), name="Padron 1964", category="Cigar", quantity=2)
    collection = Collection(name="Cigars", items=[item_a])

    storage.save_collection(collection)

    collection.items = []
    storage.save_collection(collection)

    loaded = storage.load_collection("cigars")
    assert loaded.items == []
