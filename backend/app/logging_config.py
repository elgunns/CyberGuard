"""Logging setup: console plus a log file in the logs/ folder (git-ignored).

Never pass database URLs, tokens or API keys to a logger.
"""
import logging
from pathlib import Path

LOGGER_NAME = "cyberguard"
LOG_FILE_NAME = "cyberguard.log"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(log_dir: Path, level: str = "INFO") -> None:
    """Attach console and file handlers to the 'cyberguard' logger.

    Safe to call more than once: old handlers are removed first.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)

    for old_handler in list(logger.handlers):
        logger.removeHandler(old_handler)
        old_handler.close()

    formatter = logging.Formatter(LOG_FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_dir / LOG_FILE_NAME, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(level)
    logger.propagate = False
