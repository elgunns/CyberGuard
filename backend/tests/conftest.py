"""Shared test fixtures.

Tests never use the main DATABASE_URL. They use TEST_DATABASE_URL only, and refuse
to run if that database name does not end with "_test".
"""
from urllib.parse import urlparse

import pytest

from backend.app.config import ConfigError, load_settings
from backend.app.db import connect

TABLE_NAMES = ("analyses", "parsed_events", "incidents", "ai_outputs", "sent_alerts")


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Return TEST_DATABASE_URL after checking that it is safe to use for tests."""
    try:
        settings = load_settings()
    except ConfigError as error:
        pytest.fail(str(error))

    url = settings.test_database_url
    if url is None:
        pytest.fail(
            "TEST_DATABASE_URL is not set. Add it to .env (see .env.example) "
            "before running the database tests."
        )
    if url == settings.database_url:
        pytest.fail("TEST_DATABASE_URL must not be the same as DATABASE_URL.")

    database_name = urlparse(url).path.lstrip("/")
    if not database_name.endswith("_test"):
        pytest.fail(
            f"TEST_DATABASE_URL must point to a database whose name ends with _test "
            f"(found '{database_name}')."
        )
    return url


@pytest.fixture
def empty_test_schema(test_database_url: str) -> str:
    """Drop CyberGuard's tables in the test database so each test starts clean."""
    with connect(test_database_url) as connection:
        connection.execute(
            "DROP TABLE IF EXISTS sent_alerts, ai_outputs, parsed_events, incidents, analyses CASCADE"
        )
    return test_database_url
