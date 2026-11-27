"""Error envelope and global exception handlers.

Responses look like {"success": false, "error": {"code": ..., "message": ...}}.
Stack traces are written to the log file only, never sent to the user.
"""
import logging
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("cyberguard.errors")


class ApiError(Exception):
    """Raise this in a route to return a specific error code and message."""

    def __init__(self, status_code: int, code: str, message: str,
                 details: Optional[list] = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def error_response(status_code: int, code: str, message: str,
                   details: Optional[list] = None, headers: Optional[dict] = None) -> JSONResponse:
    error = {"code": code, "message": message}
    if details:  # details only appear for validation errors
        error["details"] = details
    return JSONResponse(status_code=status_code,
                        content={"success": False, "error": error},
                        headers=headers)


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return error_response(exc.status_code, exc.code, exc.message, exc.details)


async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handles invalid query, path or body fields."""
    details = []
    for err in exc.errors():
        field = ".".join(str(p) for p in err["loc"] if p not in ("query", "path", "body"))
        details.append({"field": field or "request", "message": err["msg"]})
    return error_response(400, "VALIDATION_ERROR",
                          "The request contains invalid or missing fields.", details)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handles unknown URLs (404) and unsupported methods (405)."""
    if exc.status_code == 404:
        return error_response(404, "NOT_FOUND", "The requested endpoint does not exist.")
    if exc.status_code == 405:
        return error_response(405, "METHOD_NOT_ALLOWED",
                              "This HTTP method is not supported for this endpoint.",
                              headers=exc.headers)
    return error_response(exc.status_code, "ERROR", "The request could not be processed.")


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Logs the error (with traceback, in the log file) and returns a generic 500."""
    logger.error("Unhandled error on %s %s (%s)", request.method, request.url.path,
                 type(exc).__name__, exc_info=exc)
    return error_response(500, "INTERNAL_ERROR", "An unexpected error occurred.")


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
