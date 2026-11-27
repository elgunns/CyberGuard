"""PostgreSQL connection helper. Uses psycopg 3 with plain SQL (decision D-04)."""
import logging

import psycopg

logger = logging.getLogger("cyberguard.db")

CONNECT_TIMEOUT_SECONDS = 3


def connect(database_url: str) -> psycopg.Connection:
    """Open a connection. The caller closes it, for example with a `with` block."""
    return psycopg.connect(database_url, connect_timeout=CONNECT_TIMEOUT_SECONDS)


def is_database_reachable(database_url: str) -> bool:
    """Return True if the database answers a trivial query. Never raises."""
    try:
        with connect(database_url) as connection:
            connection.execute("SELECT 1")
        return True
    except psycopg.Error as error:
        # Log only the error class. The message or URL could contain connection details.
        logger.warning("Database health check failed (%s)", type(error).__name__)
        return False
