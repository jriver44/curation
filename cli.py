import argparse
from pathlib import Path

from services import CollectionService
from storage.base import Storage
from storage.json_storage import JsonStorage
from storage.sqlite_storage import SQLiteStorage


def _norm(s: str) -> str:
    return s.strip().casefold()


def make_storage(backend: str, db: str, json_dir: str | None = None) -> Storage:
    if backend == "sqlite":
        return SQLiteStorage(Path(db))

    if json_dir is None:
        return JsonStorage()
    return JsonStorage(Path(json_dir))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("json", "sqlite"), default="json")
    parser.add_argument("--db", default="curation.db")
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Migrate collections from one backend to another and exit",
    )
    parser.add_argument(
        "--from-backend",
        choices=("json", "sqlite"),
        default="json",
        help="Source backend for migration",
    )
    parser.add_argument(
        "--to-backend",
        choices=("json", "sqlite"),
        default="sqlite",
        help="Destination backend for migration",
    )
    parser.add_argument(
        "--json-dir",
        default=None,
        help="Directory for JSON storage (defaults to ~/.curation)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migration without writing",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=None,
        help="Migrate only these collection names (repeatable). Example: --only cigars --only tea",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite destination collections if they already exist",
    )
    args = parser.parse_args()

    if args.migrate:
        if args.from_backend == args.to_backend:
            print("Source and destination backends are the same name.\nNothing to migrate...")
            return

        source = make_storage(args.from_backend, args.db, args.json_dir)
        destination = make_storage(args.to_backend, args.db, args.json_dir)

        source_names = list(source.list_collections())
        source_existing: set[str] = {_norm(name) for name in source_names}
        destination_existing: set[str] = {_norm(name) for name in destination.list_collections()}

        requested_names = args.only if args.only else source_names

        migrated = 0
        skipped = 0
        missing = 0
        missing_names: list[str] = []
        will_migrate: list[str] = []
        seen: set[str] = set()

        for name in requested_names:
            key = _norm(name)
            if key in seen:
                continue
            seen.add(key)

            if key not in source_existing:
                missing += 1
                missing_names.append(name)
                continue

            if key in destination_existing and not args.overwrite:
                skipped += 1
                continue

            migrated += 1
            will_migrate.append(name)

            if not args.dry_run:
                destination.save_collection(source.load_collection(name))
                destination_existing.add(key)

        if args.dry_run:
            joined = ", ".join(will_migrate)
            print(f"Would migrate {migrated} collection(s): {joined}")

            if skipped or missing:
                print(f"Skipped {skipped} (exists). Missing {missing}.")
            if missing_names:
                print("Missing (not found in source): " + ", ".join(missing_names))
            return

        print(f"Migrated {migrated} collection(s). Skipped {skipped} (exists). Missing {missing}.")

        if missing_names:
            print("Missing (not found in source): " + ", ".join(missing_names))
        return

    storage: Storage = make_storage(args.backend, args.db, args.json_dir)

    service = CollectionService(storage)

    name = input("Enter collection name: ").strip()
    while not name:
        print("Name cannot be blank.")
        name = input("Enter collection name: ").strip()

    collection = service.load(name)
    print(f"Loaded collection '{name}' with {len(collection.items)} items.\n")

    while True:
        print("=== Curation ===")
        print("1) Add Item")
        print("2) Remove Item")
        print("3) Set Quantity")
        print("4) View Items")
        print("5) Summary by Category")
        print("6) Search")
        print("7) Save")
        print("8) Quit")
        choice = input("Select an option (1-7): ").strip()

        if choice == "1":
            item_name = input("Enter new item name: ").strip()
            category = input("Enter item category: ").strip()
            quant = input("Quantity to add: ").strip()

            try:
                qty = int(quant)
            except ValueError:
                print("Quantity must be an integer.")
                continue
            collection = service.add_item(collection, item_name, category, qty)
            print(f"Added '{item_name}' x{qty}.\n")

        elif choice == "2":
            name = input("Enter item name to remove: ")
            category = input("Enter item category: ")
            quantity_str = input("Quantity to remove: ")
            quantity = int(quantity_str)

            service.remove_item(collection, name, category, quantity)
            print(f"Removed '{name}' x{quantity}.")

        elif choice == "3":
            name = input("Enter item name: ")
            category = input("Enter item category: ")
            quantity_str = input("New quantity (0 deletes item from collection): ")
            quantity = int(quantity_str)

            outcome = service.set_quantity(collection, name, category, quantity)

            if outcome == "not_found":
                print("Item not found or invalid input. No changes made.")
            elif outcome == "set":
                print(f"Set '{name}' [{category}] quantity to {quantity}.")
            else:
                print(f"Deleted '{name}' [{category}].")

        elif choice == "4":
            if not collection.items:
                print("No items.\n")
                continue
            for item in collection.items:
                print(f"- {item.name} [{item.category}] x{item.quantity}")
            print()

        elif choice == "5":
            summary = service.summary_by_category(collection)
            if not summary:
                print("No items.\n")
                continue
            for cat, total in summary.items():
                print(f"{cat}: {total}")
            print()

        elif choice == "6":
            keyword = input("Search keyword: ").strip()
            results = service.search(collection, keyword)

            if not results:
                print("No matches.\n")
                continue
            for item in results:
                print(f"- {item.name} [{item.category}] x{item.quantity}")
            print()

        elif choice == "7":
            service.save(collection)
            print("Saved.\n")

        elif choice == "8":
            service.save(collection)
            print("Saved. Good Bye...")
            return

        else:
            print("Invalid option.\n")


if __name__ == "__main__":
    main()
