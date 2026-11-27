"""FastAPI application factory.

Start the server from the project root with:
    python -m uvicorn backend.app.main:create_app --factory --reload
A factory is used so that importing this module does not read .env or open logs.
"""
import logging
from typing import Optional

from fastapi import FastAPI

from backend.app.config import Settings, load_settings
from backend.app.errors import register_error_handlers
from backend.app.logging_config import configure_logging
from backend.app.routes import health

logger = logging.getLogger("cyberguard.app")


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    """Build the FastAPI app. Pass settings in tests; leave None to read the environment."""
    if settings is None:
        settings = load_settings()

    configure_logging(settings.log_dir, settings.log_level)

    app = FastAPI(
        title="CyberGuard API",
        description="AI-powered security log analyzer (backend).",
        version="0.2.0",
    )
    app.state.settings = settings
    register_error_handlers(app)
    app.include_router(health.router)

    logger.info("CyberGuard backend started")
    return app
