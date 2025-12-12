from collections import Counter
from datetime import datetime
from uuid import uuid4
from typing import Iterable
from .domain import Collection, Item
from .storage.base import Storage

class CollectionService:
    def __init__(self, storage: Storage) -> None:
        self._storage = storage
        
    def load(self, name: str) -> Collection:
        return self._storage.load_collection(name)
    
    def save(self, collection: Collection) -> None:
        self._storage.save_collection(collection)
        
    def add_item(self, collection: Collection, name: str, category: str, quantity: int) -> Collection:
        existing = next(
            (i for i in collection.items if i.name == name and i.category == category),
            None,
        )
        
        now = datetime.utcnow()
        
        if existing:
            existing.quantity += quantity
            existing.updated_at = now
        else:
            collection.items.append(
                Item(
                    id=uuid4(),
                    name=name,
                    category=category,
                    quantity=quantity,
                    created_at=now
                )
            )
        return collection
    
    def summary_by_category(self, collection: Collection) -> dict[str, int]:
        counts = Counter()
        for item in collection.items:
            counts[item.category] += item.quantity
        return dict(counts)
    
    def search(self, collection: Collection, keyword: str) -> list[Item]:
        keyword = keyword.lower()
        return [i for i in collection.items if keyword in i.name.lower()]