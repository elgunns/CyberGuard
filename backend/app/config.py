"""Settings read from environment variables and a local .env file.

Environment variables win over values in .env. Secrets are never printed:
the database URL is hidden from the repr of Settings.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_LOG_DIR = PROJECT_ROOT / "logs"
ALLOWED_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
POSTGRES_URL_PREFIXES = ("postgresql://", "postgres://")


class ConfigError(RuntimeError):
    """A required setting is missing or has an invalid value. The message is safe to show."""


@dataclass(frozen=True)
class Settings:
    database_url: str = field(repr=False)
    test_database_url: Optional[str] = field(default=None, repr=False)
    log_dir: Path = DEFAULT_LOG_DIR
    log_level: str = "INFO"


def _clean(values: Mapping[str, Optional[str]], name: str) -> Optional[str]:
    """Return the trimmed value, or None when the setting is missing or empty."""
    value = values.get(name)
    if value is None or not value.strip():
        return None
    return value.strip()


def load_settings(
    env_file: Optional[Path] = DEFAULT_ENV_FILE,
    environ: Optional[Mapping[str, str]] = None,
) -> Settings:
    """Build Settings from the .env file and the environment.

    env_file: path to a .env file, or None to skip the file.
    environ: values to use instead of os.environ (handy for tests).
    """
    file_values: dict = {}
    if env_file is not None and env_file.exists():
        file_values = {k: v for k, v in dotenv_values(env_file).items() if v is not None}

    source = os.environ if environ is None else environ
    values = {**file_values, **source}

    database_url = _clean(values, "DATABASE_URL")
    if database_url is None:
        raise ConfigError(
            "Missing required setting DATABASE_URL. Copy .env.example to .env and "
            "fill in DATABASE_URL, or set it as an environment variable."
        )
    if not database_url.startswith(POSTGRES_URL_PREFIXES):
        raise ConfigError(
            "DATABASE_URL must start with postgresql:// "
            "(format: postgresql://USER:PASSWORD@HOST:PORT/DATABASE)."
        )

    log_level = (_clean(values, "LOG_LEVEL") or "INFO").upper()
    if log_level not in ALLOWED_LOG_LEVELS:
        raise ConfigError(
            f"LOG_LEVEL must be one of {', '.join(ALLOWED_LOG_LEVELS)}."
        )

    log_dir_value = _clean(values, "LOG_DIR")
    log_dir = Path(log_dir_value) if log_dir_value else DEFAULT_LOG_DIR

    return Settings(
        database_url=database_url,
        test_database_url=_clean(values, "TEST_DATABASE_URL"),
        log_dir=log_dir,
        log_level=log_level,
    )
