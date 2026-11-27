"""Applies database/schema.sql to the database named in DATABASE_URL.

Run from the project root:
    python database/init_db.py
"""
import sys
from pathlib import Path

# Make the project root importable when this file runs as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import psycopg  # noqa: E402

from backend.app.config import ConfigError, load_settings  # noqa: E402
from backend.app.db import connect  # noqa: E402

SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"


def apply_schema(database_url: str) -> None:
    """Run every statement in schema.sql inside one transaction."""
    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
    with connect(database_url) as connection:
        connection.execute(schema_sql)


def main() -> int:
    try:
        settings = load_settings()
    except ConfigError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    try:
        apply_schema(settings.database_url)
    except psycopg.Error as error:
        print(
            f"Error: could not apply the schema ({type(error).__name__}). "
            "Check DATABASE_URL and that the database exists.",
            file=sys.stderr,
        )
        return 1

    print("Schema applied successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
