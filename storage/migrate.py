from __future__ import annotations

from storage.base import Storage


def migrate_all(source: Storage, destination: Storage) -> int:
    """
    Copies all collections from source storage to destination storage.

    Returns the number of collections migrated.
    """

    count = 0
    for name in source.list_collections():
        collection = source.load_collection(name)
        destination.save_collection(collection)
        count += 1
    return count
