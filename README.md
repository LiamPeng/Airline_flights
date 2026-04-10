# Airline flights (Flask + Postgres)

Small web app for the airline DB assignment. Backend is Postgres with the course schema; front end is Flask and Jinja. You enter origin/destination airport codes and a date range, get a list of flights, then click one to see capacity, how many seats are booked, and how many are left.

## The two SQL files

**`schema.sql`** — creates tables (with foreign keys). Run:

`python app.py --init-db`

**`flights.sql`** — sample data only (`INSERT`s). Run after init:

`python app.py --load-sample-data`

If `flights.sql` still contains `CREATE TABLE` from an old one-file homework dump, don’t run that after `--init-db` or you’ll hit “relation already exists”. I split schema and data so the structure matches the ER diagram with proper FKs.

## Environment

You need Postgres and a database (e.g. `createdb airline`). Then set:

```bash
export DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/airline"
```

Use your real username and password — don’t leave literal `...` in the URL or the client will fail in a confusing way. On a Mac with local trust/peer auth, this often works:

```bash
export DATABASE_URL="postgresql:///airline"
```

`AIRLINE_DATABASE_URL` works the same as `DATABASE_URL` if you prefer that name.

## First-time setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://..."   # your connection string
python app.py --init-db
python app.py --load-sample-data
```

If the DB is a mess, `dropdb` / `createdb` and run the last two lines again.

## Demo day

```bash
export DATABASE_URL="postgresql://..."
python app.py
```

Open http://127.0.0.1:5000 . If you loaded this repo’s `flights.sql`, try JFK → LAX with a range that includes 2026 (the seed has flights in 2025 and 2026).

## Routes (for the write-up)

| Path | What it does |
|------|----------------|
| `GET /` | Search form |
| `POST /search` | Validates input, redirects to results |
| `GET /flights?...` | Flight list |
| `GET /flights/<flight_number>/<date>` | Seat summary for that flight/date |

Dates are `YYYY-MM-DD`; the range is inclusive. Departure times are shown as stored in the DB (treated as GMT).
