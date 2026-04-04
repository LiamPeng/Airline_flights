# Airline Flights and Booking (Flask + PostgreSQL)

Simple Flask web app for searching flights by route and date range, then viewing seat availability for a selected flight/date.

## Features

- Start page form for `origin_code`, `dest_code`, `start_date`, `end_date`.
- Flight results page shows all matching flights (including fully booked flights).
- Click a flight to view plane capacity, booked seats, and available seats.

## Database: which SQL file to use?

| File | Role |
|------|------|
| **`schema.sql`** | **Table definitions** for PostgreSQL, including **foreign keys** matching the ER diagram. Use this with `python app.py --init-db`. |
| **`flights.sql`** | **Sample INSERT data** (homework-style dataset). Load **after** the schema is created: `python app.py --load-sample-data` or `psql "$DATABASE_URL" -f flights.sql`. |

The original single-file homework dump mixed CREATE + data **without** foreign keys. This project keeps **`schema.sql` as the single source of truth for structure** (with FKs) and **`flights.sql` for optional seed data** so you do not duplicate conflicting DDL.

## Configuration

- Engine: **PostgreSQL**
- Connection string (required). **Do not** use the literal text `...` from examples; put your real username, password, and database name.

```bash
# Typical local Postgres (replace myuser / mypass with your roles)
export DATABASE_URL="postgresql://myuser:mypass@localhost:5432/airline"
```

If your Mac user can connect without a password (peer/trust), you can use:

```bash
export DATABASE_URL="postgresql:///airline"
```

(`AIRLINE_DATABASE_URL` is accepted as an alias.)

## Setup

1. Create a database (e.g. `createdb airline` or via your host’s UI).
2. Virtual environment (optional):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create tables:

   ```bash
   export DATABASE_URL="postgresql://pengminyi@localhost:5432/airline"
   python app.py --init-db
   ```

5. (Optional) Load sample data from `flights.sql`:

   ```bash
   python app.py --load-sample-data
   ```

## Run

```bash
export DATABASE_URL="postgresql://pengminyi@localhost:5432/airline"
python app.py
```

Open `http://127.0.0.1:5000`.

## Routes

- `GET /` — search form
- `POST /search` — validates and redirects to results
- `GET /flights` — matching flights
- `GET /flights/<flight_number>/<departure_date>` — capacity and available seats

## Notes

- Date format: `YYYY-MM-DD`; range is **inclusive**.
- Departure times are shown as stored (assumed GMT).
