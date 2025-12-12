from typing import Protocol, Iterable
from domain import Collection

class Storage(Protocol):
    def list_collections(self) -> Iterable[str]:
        ...
    
    def load_collection(self, name: str) -> Collection:
        ...
    
    def save_collection(self, collection: Collection) -> None:
        ...