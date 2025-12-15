# Curation

Curation is a small inventory/collection tracker I'm building in Python

Right now it's a simple CLI app that lets me track simple things by category. Long-term, it's also my "lab project" to practice for my final semester over the winter break.

This repo is where I'll glue all that class content onto one evolving project instead of writting five disconnected throwaway programs.

---

## What it does (12/11/2025)

Current version is intentionally small and clean:

- CLI-based interface
- Add items with:
  - `name`
  - `category`
  - `quantity`
- View all items
- Summary by category (totals per category)
- Simple keyword search
- JSON-based storage using a `Storage` abstraction

So it's already usable as a minimal collection tracker, but the real point is to constantly grow the app.

---

## Why this exists

I realized I'd accidentally stacked my schedule with:

- Software Engineering
- Intro to Databases
- Intro to Cybersecurity
- Operating Systems
- Numeric Computing

Instead of letting those live as five seperate practice assignments, I'm using **Curation** as a single, evolving codebase to:

- Practice "real" SE habits (issues, refactors, tests, docs)
- Add an actual database layer (SQLite)
- Think about security and misue
- Touch some OS concepts (files, maybe some concurrency later)
- Do some basic stats / numeric analysis on collection data.

This way, everything I learn has a home in one project I care about.

---

## Tech stack

- **Language:** Python 3.x
- **Interface:** CLI
- **Storage:** JSON files via `Storage` interface (will be changed once SQLite is implemented)
- **Testing:** `pytest`

---

## Getting started

### 1. Clone the repo

SSH:
```bash
git clone git@github.com-jriver44:jriver44/curation.git
cd curation
```

or HTTPS:
```bash
git clone https://github.com/jriver44/curation.git
cd curation
```

### 2. Set up a virtual enviroment
```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### 3. Run the CLI
From the project root:
```bash
python -m curation.cli
```

This will prompt for a collection name:
- If it exists, it loads.
- If not, it starts a new collection and saves to a JSON file under ~/.curation/

Then you will see a menu like:
```bash
=== Curation ===
1) Add Item
2) View Items
3) Summary by Category
4) Search
5) Save
6) Quit
```

This is barebones for now, but will be improved as it evolves.

---

## How this connects to my future semester (plan for studying)

### 1. Software Engineering
Use curation as the "project" for SE topics:
- Write and maintain a ROADMAP.md
- Add proper docstrings and comments
- Introduce pytest tests (domain + storage)
- Use feature branches and clean commit history
- Do small, intentional refactors 

### 2. Intro to Databases
I want to move beyond JSON:
- Design a simple SQLite schema for items and categories
- Implement a SQLiteStorage backend alongside JsonStorage
- Migrate or import existing JSON collections into DB.
- Practice basic queries directly via Python

### 3. Intro to Cybersecurity
Think about this assignment as if it wer multi-user / networked, even with local implementation as of now:
- Harden input validation
- Add simple logging of operations
- Start a small threat model:
  - What happens if someone tampers with the JSON/DB?
  - What data would actually need to be protected?
- Maybe down the line: auth / profiles

### 4. Operating Systems
Use Curation to practice OS concepts:
- Delibrit file I/O patterns
- Safe writes (atomic saving)
- Maybe an autosave or background task later
- Config files, enviroment-based settings, etc.

### 5. Numeric Computing
Turn the collection data into something we can analyze:
- Export counts and categories in a numeric-friendly form
- Compute simple stats:
  - Items per category
  - Totals over time (history will be added later)
- Plug in vectoriezed operations or basic numeric routines


All of this was researched from old syllabi found online. 

---

## Roadmap

### Phase 1: Rewrite from v1:
- Minimal CLI with JSON storage
- Add basic tests (domain & storage)
- Clean up CLI vs domain seperation
- Document architecture & module responsibilities

### Phase 2: Database:
- Add SQLite backend
- Schema design + migrations / imports
- Config option to choose storage backend

### Phaswe 3: Security and OS
- Input validation and error handling
- Basic logging
- Safer file operations / atomic writes

### Phase 4: Numeric / Analytics
- Export collection data in numeric form
- Basic stats and summaries

Will look at the future of the app, and how I can use it more to understand my classes after Phase 4.

---

## Status as of 12/11/2025:
- CLI works
- Core domain model exists
- Repo is clean
- README composed


## Status as of 12/14/2025:
- Built out services.py (CollectionService)
  - load(name) / save(collection) working through a storage abstraction
  - add_item() working + increments quantity on duplicates
  - remove_item() working + decrements + removes entry at zero
  - summary_by_category() working
  - search() working
- Added normalization (_norm) so matching/search can be case-insensitive without messing with the display formatting.
- Tightened input validation:
  - Reject blank names/categories (whitespace and empty)
  - Reject zero/negative quantities for add/remove
- Testing:
  - add item creates entry
  - add item increments quantity
  - remove item partial + exact removal
  - remove nonexistent does nothing
  - rejects blank fields
  - rejects invalid quantities
  - summary category totals
  - case-insensitive behavior
- Many tests hit multiple failures, but have been brought up to snuff.
- Repo/tools:
  - Rebuilt git
  - Added .gitignore (venv, pycache, macOS stuff)
  - Cleaned up ssh keys that I had added by mistake
- Documentation:
  - README updated to match current project scope
  - Architecture updated so it no longer claims remove/search/summary are future work.
- Final state as of 12/14/2025:
  - App runs
  - Tests are green
  - Architecture layered correctly (domain/service/storage/cli)
  - Docs match the code

---