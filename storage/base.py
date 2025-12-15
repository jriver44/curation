from collections.abc import Iterable
from typing import Protocol

from domain import Collection


class Storage(Protocol):
    def list_collections(self) -> Iterable[str]: ...

    def load_collection(self, name: str) -> Collection: ...

    def save_collection(self, collection: Collection) -> None: ...
