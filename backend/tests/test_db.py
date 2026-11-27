"""Tests for the schema (database/schema.sql). They use TEST_DATABASE_URL only."""
import psycopg
import pytest

from backend.app.db import connect
from database.init_db import apply_schema

TABLE_NAMES = ("analyses", "parsed_events", "incidents", "ai_outputs", "sent_alerts")


def _existing_tables(database_url: str) -> set:
    with connect(database_url) as connection:
        rows = connection.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = ANY(%s)",
            (list(TABLE_NAMES),),
        ).fetchall()
    return {row[0] for row in rows}


def test_schema_creates_all_tables_in_test_database(empty_test_schema: str):
    assert _existing_tables(empty_test_schema) == set()

    apply_schema(empty_test_schema)

    assert _existing_tables(empty_test_schema) == set(TABLE_NAMES)


def test_schema_can_be_applied_twice(empty_test_schema: str):
    apply_schema(empty_test_schema)
    apply_schema(empty_test_schema)

    assert _existing_tables(empty_test_schema) == set(TABLE_NAMES)


def test_severity_check_rejects_unknown_value(empty_test_schema: str):
    apply_schema(empty_test_schema)
    with connect(empty_test_schema) as connection:
        analysis_id = connection.execute(
            "INSERT INTO analyses (original_filename, file_size_bytes) "
            "VALUES ('sample.log', 10) RETURNING id"
        ).fetchone()[0]

    with pytest.raises(psycopg.errors.CheckViolation):
        with connect(empty_test_schema) as connection:
            connection.execute(
                "INSERT INTO incidents (analysis_id, incident_type, severity, title, "
                "event_count, evidence) VALUES (%s, 'FAILED_LOGIN_BURST', 'Severe', "
                "'test', 1, 'test')",
                (analysis_id,),
            )
