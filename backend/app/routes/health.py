"""GET /health (FR-24): reports backend and database status."""
from fastapi import APIRouter, Request

from backend.app.db import is_database_reachable
from backend.app.responses import success_response

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check(request: Request):
    """Returns 200 when the database answers, or 503 with status "degraded" when it does not."""
    database_url = request.app.state.settings.database_url
    database_ok = is_database_reachable(database_url)

    data = {
        "status": "ok" if database_ok else "degraded",
        "backend": "ok",
        "database": "ok" if database_ok else "unreachable",
    }
    if database_ok:
        return success_response(data, "CyberGuard backend and database are running.")
    return success_response(
        data,
        "The database is unreachable. The backend is running in degraded mode.",
        status_code=503,
    )
