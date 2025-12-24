from pathlib import Path

from cli import make_storage
from storage.json_storage import JsonStorage
from storage.sqlite_storage import SQLiteStorage


def test_make_storage_json(tmp_path: Path) -> None:
    storage = make_storage("json", str(tmp_path / "x.db"))
    assert isinstance(storage, JsonStorage)


def test_make_storage_sqlite(tmp_path: Path) -> None:
    storage = make_storage("sqlite", str(tmp_path / "curation.db"))
    assert isinstance(storage, SQLiteStorage)
