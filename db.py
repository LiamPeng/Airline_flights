import os
from pathlib import Path
from urllib.parse import urlparse

import psycopg
from psycopg.rows import dict_row


def get_dsn() -> str:
    dsn = os.getenv("DATABASE_URL") or os.getenv("AIRLINE_DATABASE_URL")
    if not dsn:
        raise RuntimeError(
            "Set DATABASE_URL (or AIRLINE_DATABASE_URL) to a PostgreSQL connection string, "
            "e.g. postgresql://user:pass@localhost:5432/airline"
        )
    dsn = dsn.strip()
    if "..." in dsn:
        raise RuntimeError(
            "DATABASE_URL must not contain the literal placeholder '...'. "
            "Replace USER, PASSWORD, host, and database name with your real values. "
            "Example: postgresql://myuser:mypass@localhost:5432/airline "
            "Or for local trust/peer auth: postgresql:///airline"
        )
    parsed = urlparse(dsn)
    if parsed.scheme not in ("postgresql", "postgres"):
        raise RuntimeError(
            f"DATABASE_URL must use scheme postgresql:// (got scheme {parsed.scheme!r})."
        )
    host = parsed.hostname
    if host == "...":
        raise RuntimeError(
            "DATABASE_URL host cannot be '...'. Use a real hostname such as localhost."
        )
    if host is None and not (parsed.path or "").strip("/"):
        raise RuntimeError(
            "DATABASE_URL must include a database name, e.g. postgresql:///airline or "
            "postgresql://localhost:5432/airline"
        )
    return dsn


def get_connection() -> psycopg.Connection:
    return psycopg.connect(get_dsn(), row_factory=dict_row)


# For init_db and load_sample_data
def execute_sql_file(conn: psycopg.Connection, path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    lines: list[str] = []
    for line in raw.splitlines():
        if line.strip().startswith("--"):
            continue
        lines.append(line)
    text = "\n".join(lines)
    for stmt in text.split(";"):
        stmt = stmt.strip()
        if stmt:
            conn.execute(stmt)


def query_all(sql: str, params: tuple | list = ()) -> list:
    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return rows


def query_one(sql: str, params: tuple | list = ()) -> object | None:
    with get_connection() as conn:
        row = conn.execute(sql, params).fetchone()
    return row
