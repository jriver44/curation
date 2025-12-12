from collections import Counter
from datetime import datetime
from uuid import uuid4
from typing import Iterable
from domain import Collection, Item
from storage.base import Storage
from storage.json_storage import JsonStorage

class CollectionService:
    def __init__(self, storage: Storage | None = None):
        """
        If 'storage' is not provided, default to JsonStorage.
        
        This makes it easy to use in tests:
            svc = CollectionServices()
        and in the CLI:
            svc = CollectionServices(JsonStorage())
        """
        self._storage = storage or JsonStorage()
        
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
    
    def remove_item(self, collection: Collection, name: str, category: str, quantity: int) -> Collection:
        existing = next(
            (i for i in collection.items if i.name == name and i.category == category),
            None,
        )
        
        if existing is None:
            print("Item doesn't exist inside collection.\n")
            return collection
        
        if quantity <= 0:
            print("Can't update quantity with 0 or negatives")
            return collection
        
        now = datetime.utcnow()
        
        if existing.quantity > quantity:
            existing.quantity -= quantity
            existing.updated_at = now
        else:
            print("Removing item from collection (x0 quantity)")
            collection.items.remove(existing)
            
        return collection
    
    def summary_by_category(self, collection: Collection) -> dict[str, int]:
        counts = Counter()
        for item in collection.items:
            counts[item.category] += item.quantity
        return dict(counts)
    
    def search(self, collection: Collection, keyword: str) -> list[Item]:
        keyword = keyword.lower()
        return [i for i in collection.items if keyword in i.name.lower()]