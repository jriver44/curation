from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from domain import Collection, Item
from storage.json_storage import JsonStorage
from storage.migrate import migrate_all
from storage.sqlite_storage import SQLiteStorage


def _items_as_logical_set(collection: Collection) -> set[tuple[str, str, int]]:
    return {(i.name, i.category, i.quantity) for i in collection.items}


def test_migrate_json_to_sqlite_roundtrip(tmp_path: Path) -> None:
    json_dir = tmp_path / "json"
    db_path = tmp_path / "curation.db"

    source = JsonStorage(json_dir)
    destination = SQLiteStorage(db_path)

    source_collection = Collection(
        name="Cigars",
        items=[
            Item(id=uuid4(), name="Padron 1964", category="Cigar", quantity=2),
            Item(id=uuid4(), name="Trinidad", category="Cigar", quantity=1),
        ],
    )

    source.save_collection(source_collection)

    assert list(source.list_collections()) == ["Cigars"]

    migrated_collection = migrate_all(source, destination)
    assert migrated_collection == 1

    loaded = destination.load_collection("cigars")
    assert loaded.name == "Cigars"
    assert _items_as_logical_set(loaded) == _items_as_logical_set(source_collection)


def test_migration_is_idempotent(tmp_path: Path) -> None:
    json_dir = tmp_path / "json"
    db_path = tmp_path / "curation.db"

    source = JsonStorage(json_dir)
    destination = SQLiteStorage(db_path)

    source.save_collection(
        Collection(
            name="Tea",
            items=[Item(id=uuid4(), name="Da Hong Pao", category="Oolong", quantity=3)],
        )
    )

    assert list(source.list_collections()) == ["Tea"]

    migrate_all(source, destination)
    migrate_all(source, destination)

    loaded = destination.load_collection("tea")
    assert _items_as_logical_set(loaded) == {("Da Hong Pao", "Oolong", 3)}
