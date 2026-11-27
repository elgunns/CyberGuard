"""Tests for backend/app/config.py. These need no database."""
from pathlib import Path

import pytest

from backend.app.config import ConfigError, load_settings

VALID_URL = "postgresql://cyberguard_user:secret-pass-123@127.0.0.1:5432/cyberguard"


def test_reads_database_url_from_environment():
    settings = load_settings(env_file=None, environ={"DATABASE_URL": VALID_URL})
    assert settings.database_url == VALID_URL
    assert settings.log_level == "INFO"


def test_missing_database_url_gives_clear_error():
    with pytest.raises(ConfigError) as info:
        load_settings(env_file=None, environ={})
    message = str(info.value)
    assert "DATABASE_URL" in message
    assert ".env.example" in message


def test_empty_database_url_counts_as_missing():
    with pytest.raises(ConfigError, match="DATABASE_URL"):
        load_settings(env_file=None, environ={"DATABASE_URL": "   "})


def test_reads_values_from_dotenv_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(f"DATABASE_URL={VALID_URL}\nLOG_LEVEL=debug\n", encoding="utf-8")

    settings = load_settings(env_file=env_file, environ={})

    assert settings.database_url == VALID_URL
    assert settings.log_level == "DEBUG"


def test_environment_variable_overrides_dotenv_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=postgresql://from-file/db\n", encoding="utf-8")

    settings = load_settings(env_file=env_file, environ={"DATABASE_URL": VALID_URL})

    assert settings.database_url == VALID_URL


def test_invalid_log_level_is_rejected():
    with pytest.raises(ConfigError, match="LOG_LEVEL"):
        load_settings(env_file=None, environ={"DATABASE_URL": VALID_URL, "LOG_LEVEL": "LOUD"})


def test_database_url_must_be_postgres():
    with pytest.raises(ConfigError, match="postgresql://"):
        load_settings(env_file=None, environ={"DATABASE_URL": "mysql://user@host/db"})


def test_settings_repr_hides_database_password():
    settings = load_settings(env_file=None, environ={"DATABASE_URL": VALID_URL})
    assert "secret-pass-123" not in repr(settings)
