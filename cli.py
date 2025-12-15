from services import CollectionService
from storage.json_storage import JsonStorage


def main() -> None:
    storage = JsonStorage()
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
        print("2) View Items")
        print("3) Summary by Category")
        print("4) Search")
        print("5) Save")
        print("6) Quit")
        choice = input("Select an option (1-6): ").strip()

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
            if not collection.items:
                print("No items.\n")
                continue
            for item in collection.items:
                print(f"- {item.name} [{item.category}] x{item.quantity}")
            print()

        elif choice == "3":
            summary = service.summary_by_category(collection)
            if not summary:
                print("No items.\n")
                continue
            for cat, total in summary.items():
                print(f"{cat}: {total}")
            print()

        elif choice == "4":
            keyword = input("Search keyword: ").strip()
            results = service.search(collection, keyword)

            if not results:
                print("No matches.\n")
                continue
            for item in results:
                print(f"- {item.name} [{item.category}] x{item.quantity}")
            print()

        elif choice == "5":
            service.save(collection)
            print("Saved.\n")

        elif choice == "6":
            service.save(collection)
            print("Saved. Good Bye...")
            return

        else:
            print("Invalid option.\n")


if __name__ == "__main__":
    main()
