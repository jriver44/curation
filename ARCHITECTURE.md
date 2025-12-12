# Curation Architecture - Winter 2025 Baseline

## Goal

Curation is a small collection tracker built as a practice project for:
- Software Engineering
- Intro to Database
- Intro to Cybersecurity
- Operating Systems
- Numeric Computing
  
The design is intentionally simple but layered so I can swap pieces out (storage backend, UI, analysis) over time.

## Modules

- `domain.py`
  - Core data model:
    - `Item`: id, name, category, quantity, timestamps.
    - `Collection`: name + list of `Item`s.
  - No I/O. Just data + helpers.

- `services.py`
  - `CollectionService`:
    - `add_item(collection, name, category, quantity) -> Collection`
    - (More methods will be added over time from v1: remove, search, summary, etc.)
  - Orchestrates domain + storage.
  - Business rules live here, not in the CLI.

- `storage/`
  - `base.py`
    - `Storage` protocol: `list_collections`, `load_colleciton`, `save_colleciton`.
  - `json_storage.py`
    - `JsonStorage`: saves/loads `Collection` to JSON files in a data directory.
  - Later I will grow this to include a Database-backed storage class.

- `cli.py`
  - Simple terminal UI:
    - Prompt for collection name.
    - Menu for add, view, summary, search, save, quit.
  - Calls `CollectionService` methods and prints results.

- `tests/`
  - `test_domain.py`
    - Tests `CollectionService.add_item`:
      - creates new items with correct fields.
      - increments quantity when the same item is added again.

## Invariants (as of 12/11/2025)

- The CLI never touches disk directly. Persistence goes through `Storage`.
- Domain objects (`Item`, `Collection`) do not print or read from input.
- Business logic lives in `CollecitonServices`, not inside the CLI or storage.
- Tests should talk to `CollectionServices` and domain types.

## Future study hooks

- **Software Engineering**
  - Add more service methods and tests (remove, search, category summaries).
  - Add logging, error handling, and maybe configuration.

- **Databases**
  - Implement a `SqlStorage` that satisfies `Storage` against SQLite
  - Compare behaviors vs `JsonStorage`.

- **Cybersecurity**
  - Harden input handling and validation in the CLI.
  - Think about trust boundaries between user input, service, and storage.

- **Operating Systems**
  - Look at file I/O patterns in `JsonStorage`.
  - Consider concurrency / locking if multiple processes ever modify collections.

- **Numeric Computing**
  - Analytics / stats on collections (counts, distributions, trends).