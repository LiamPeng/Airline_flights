from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

from db import execute_sql_file, get_connection, query_all, query_one


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


def parse_date(value: str) -> datetime.date | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def validate_search_inputs(
    origin_code: str, dest_code: str, start_date: str, end_date: str
) -> tuple[dict[str, str], dict[str, str]]:
    errors: dict[str, str] = {}
    cleaned = {
        "origin_code": origin_code.strip().upper(),
        "dest_code": dest_code.strip().upper(),
        "start_date": start_date.strip(),
        "end_date": end_date.strip(),
    }

    if len(cleaned["origin_code"]) != 3:
        errors["origin_code"] = "Origin airport code must be 3 characters."

    if len(cleaned["dest_code"]) != 3:
        errors["dest_code"] = "Destination airport code must be 3 characters."

    start = parse_date(cleaned["start_date"])
    end = parse_date(cleaned["end_date"])
    if start is None:
        errors["start_date"] = "Start date must use YYYY-MM-DD format."
    if end is None:
        errors["end_date"] = "End date must use YYYY-MM-DD format."
    if start and end and start > end:
        errors["date_range"] = "Start date must be earlier than or equal to end date."

    return cleaned, errors


# Homepage route
@app.get("/")
def index():
    return render_template("index.html", errors={}, values={})


@app.post("/search")
def search():
    cleaned, errors = validate_search_inputs(
        request.form.get("origin_code", ""),
        request.form.get("dest_code", ""),
        request.form.get("start_date", ""),
        request.form.get("end_date", ""),
    )

    if errors:
        return render_template("index.html", errors=errors, values=cleaned), 400

    return redirect(
        url_for(
            "flights",
            origin_code=cleaned["origin_code"],
            dest_code=cleaned["dest_code"],
            start_date=cleaned["start_date"],
            end_date=cleaned["end_date"],
        )
    )


@app.get("/flights")
def flights():
    cleaned, errors = validate_search_inputs(
        request.args.get("origin_code", ""),
        request.args.get("dest_code", ""),
        request.args.get("start_date", ""),
        request.args.get("end_date", ""),
    )

    if errors:
        return render_template("index.html", errors=errors, values=cleaned), 400

    rows = query_all(
        """
        SELECT
          f.flight_number,
          f.departure_date,
          fs.origin_code,
          fs.dest_code,
          fs.departure_time
        FROM Flight AS f
        JOIN FlightService AS fs
          ON fs.flight_number = f.flight_number
        WHERE fs.origin_code = %s
          AND fs.dest_code = %s
          AND f.departure_date BETWEEN %s AND %s
        ORDER BY f.departure_date ASC, fs.departure_time ASC, f.flight_number ASC
        """,
        (
            cleaned["origin_code"],
            cleaned["dest_code"],
            cleaned["start_date"],
            cleaned["end_date"],
        ),
    )

    return render_template("results.html", flights=rows, filters=cleaned)


@app.get("/flights/<flight_number>/<departure_date>")
def flight_detail(flight_number: str, departure_date: str):
    if parse_date(departure_date) is None:
        abort(400, description="Invalid departure date format.")

    details = query_one(
        """
        SELECT
          f.flight_number,
          f.departure_date,
          f.plane_type,
          fs.origin_code,
          fs.dest_code,
          fs.departure_time,
          a.capacity,
          (
            SELECT COUNT(*)
            FROM Booking AS b
            WHERE b.flight_number = f.flight_number
              AND b.departure_date = f.departure_date
          ) AS booked_count
        FROM Flight AS f
        JOIN FlightService AS fs
          ON fs.flight_number = f.flight_number
        JOIN Aircraft AS a
          ON a.plane_type = f.plane_type
        WHERE f.flight_number = %s
          AND f.departure_date = %s
        """,
        (flight_number, departure_date),
    )

    if details is None:
        abort(404, description="Flight not found for the provided date.")

    capacity = int(details["capacity"])
    booked = int(details["booked_count"])
    available = max(capacity - booked, 0)

    return render_template(
        "flight_detail.html",
        details=details,
        capacity=capacity,
        booked=booked,
        available=available,
    )


def init_db() -> None:
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    with get_connection() as conn:
        execute_sql_file(conn, schema_path)
        conn.commit()


def load_sample_data() -> None:
    data_path = Path(__file__).resolve().parent / "flights.sql"
    with get_connection() as conn:
        execute_sql_file(conn, data_path)
        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Airline flights Flask app")
    parser.add_argument(
        "--init-db", action="store_true", help="Initialize the PostgreSQL database schema"
    )
    parser.add_argument(
        "--load-sample-data",
        action="store_true",
        help="Load sample rows from flights.sql (run after --init-db on an empty DB)",
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Flask host for development server"
    )
    parser.add_argument(
        "--port", default=5000, type=int, help="Flask port for development server"
    )
    args = parser.parse_args()

    if args.init_db:
        init_db()
        print("Initialized database schema (PostgreSQL).")
        return

    if args.load_sample_data:
        load_sample_data()
        print("Loaded sample data from flights.sql.")
        return

    app.run(host=args.host, port=args.port, debug=True)


if __name__ == "__main__":
    main()

