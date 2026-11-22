# DealerOS Reconciliation

DealerOS is a Django + React app that imports System A and System B CSV records, compares them, and exposes tenant-safe disagreement rows in a small table.

## Run from a clean clone

Windows PowerShell:

```powershell
cd dealeros
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

cd backend
python manage.py migrate
python manage.py import_data
python manage.py runserver
```

In a second terminal:

```powershell
cd dealeros\frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Tests

```powershell
cd backend
pytest -q
```

## CSV input

Place these three files in `backend/data/`:

- `locations.csv`
- `system_a.csv`
- `system_b.csv`

The CSV files are not included in this workspace snapshot, so they must be supplied before importing real records. The importer keeps every saved row, stores blank or invalid B values as null, and uses `update_or_create` for repeatable imports.

## What was deliberately not built

- Authentication
- Pagination
- Docker
- Advanced styling
- Authorization roles beyond the explicit `org` query parameter

## How I worked with the agent

I used Copilot to separate the work into models, importer, pure comparison logic, API, frontend, and tests. I reviewed each implementation and ran migrations and pytest. I also checked that dirty values are parsed as null or cleaned rather than converted to zero, and that importer counts are visible in command output.

## Three answers

### a. One thing the AI agent got wrong

The initial importer command path in one draft would have looked in the wrong parent directory for `backend/data`. I noticed it while reading the command path and corrected it to the backend directory. The fix was verified against the expected `backend/data/<file>.csv` layout.

### b. Least confident part

The cross-organization location case is the least confident part. The API hides a foreign B location and attributes A-side rows to the A location org, but I would validate this against every real trap row and extend the response shape only if needed.

### c. If I had a second day

I would first add fixture-based importer tests using the supplied real CSV files, because exact row counts and dirty-row behavior are the strongest correctness checks. This would catch a missed row or accidental conversion to zero more reliably than only unit-testing helpers.
