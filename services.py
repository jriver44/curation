from collections import Counter
from datetime import datetime
from uuid import uuid4

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
        name = _norm(name)
        return self._storage.load_collection(name)

    def save(self, collection: Collection) -> None:
        self._storage.save_collection(collection)

    def add_item(
        self, collection: Collection, name: str, category: str, quantity: int
    ) -> Collection:
        norm_name = _norm(name)
        norm_category = _norm(category)

        if not norm_name or not norm_category or quantity <= 0:
            return collection

        disp_name = _clean_display(name)
        disp_category = _clean_display(category)

        existing = next(
            (
                i
                for i in collection.items
                if _norm(i.name) == norm_name and _norm(i.category) == norm_category
            ),
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
                    name=disp_name,
                    category=disp_category,
                    quantity=quantity,
                    created_at=now,
                )
            )
        return collection

    def remove_item(
        self, collection: Collection, name: str, category: str, quantity: int
    ) -> Collection:
        if quantity <= 0:
            return collection

        norm_name = _norm(name)
        norm_category = _norm(category)

        existing = next(
            (
                i
                for i in collection.items
                if _norm(i.name) == norm_name and _norm(i.category) == norm_category
            ),
            None,
        )

        if existing is None:
            return collection

        now = datetime.utcnow()

        if existing.quantity > quantity:
            existing.quantity -= quantity
            existing.updated_at = now
        else:
            collection.items.remove(existing)

        return collection

    def summary_by_category(self, collection: Collection) -> dict[str, int]:
        counts = Counter()
        for item in collection.items:
            counts[item.category] += item.quantity
        return dict(counts)

    def search(self, collection: Collection, keyword: str) -> list[Item]:
        if keyword.strip() == "":
            return []

        key = _norm(keyword)
        return [i for i in collection.items if key in _norm(i.name)]


def _norm(s: str) -> str:
    return s.strip().casefold()


def _clean_display(s: str) -> str:
    return s.strip()
