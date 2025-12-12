import json
import os
from pathlib import Path
from uuid import UUID
from datetime import datetime
from typing import Iterable
from storage.base import Storage
from domain import Collection, Item

DATA_DIR = Path(os.environ.get("CURATION_DATA_DIR", Path.home() / ".curation"))

class JsonStorage(Storage):
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or DATA_DIR
        self.root.mkdir(parents=True, exist_ok=True)
        
    def _path_for(self, name: str) -> Path:
        return self.root / f"{name}.json"
    
    def list_collections(self) -> Iterable[str]:
        for p in self.root.glob("*.json"):
            yield p.stem
            
    def load_collection(self, name: str) -> Collection:
        path = self._path_for(name)
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
                    datetime.fromisoformat(item["updated_at"])
                    if item.get("updated_at")
                    else None
                ),
            )
            for item in raw.get("items", [])
        ]
        return Collection(name=name, items=items)
    
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