from __future__ import annotations

import json
import os
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from uuid import UUID

from domain import Collection, Item
from storage.base import Storage

DATA_DIR = Path(os.environ.get("CURATION_DATA_DIR", Path.home() / ".curation"))

def _norm(s: str) -> str:
    return s.strip().casefold()

class JsonStorage(Storage):
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = (
            (Path.home() / ".curation") if data_dir is None else Path(data_dir)
        )
        self._data_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, name: str) -> Path:
        return self._data_dir / f"{name}.json"

    def list_collections(self) -> Iterable[str]:
        self._data_dir.mkdir(parents=True, exist_ok=True)

        names: list[str] = []

        for path in sorted(self._data_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                # skip corrupted/unreadable files
                continue

            name = payload.get("name")

            if isinstance(name, str) and name.strip():
                names.append(name)

        return names

    def load_collection(self, name: str) -> Collection:
        path = self._path_for(name)
        legacy = self._data_dir / f"{name}.json"
        
        if not path.exists() and legacy.exists():
            path = legacy
        
        if not path.exists():
            return Collection(name=name)

        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        items = [
            Item(
                id=UUID(item["id"]),
                name=item["name"],
                category=item["category"],
                quantity=item["quantity"],
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=(
                    datetime.fromisoformat(item["updated_at"]) if item.get("updated_at") else None
                ),
            )
            for item in raw.get("items", [])
        ]
        
        display_name = raw.get("name", name)
        return Collection(name=display_name, items=items)

    def save_collection(self, collection: Collection) -> None:
        path = self._path_for(collection.name)
        temp = path.with_suffix(".tmp")

        payload = {
            "name": collection.name,
            "items": [
                {
                    "id": str(item.id),
                    "name": item.name,
                    "category": item.category,
                    "quantity": item.quantity,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                }
                for item in collection.items
            ],
        }

        with temp.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp, path)
        

