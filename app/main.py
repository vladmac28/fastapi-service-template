from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import err
from app.core.logging import setup_logging
from app.core.middleware import RequestIdMiddleware

setup_logging()

app = FastAPI(title=settings.app_name)
app.add_middleware(RequestIdMiddleware)
app.include_router(api_router)


def _request_id(request: Request) -> str:
    rid = getattr(request.state, "request_id", None)
    return rid or "unknown"


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    rid = _request_id(request)
    detail = exc.detail

    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        payload = detail
    elif isinstance(detail, str):
        payload = err("http_error", detail)
    else:
        payload = err("http_error", "Request failed.", details=detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": payload, "request_id": rid},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    rid = _request_id(request)
    return JSONResponse(
        status_code=422,
        content={
            "error": err("validation_error", "Invalid request.", details=exc.errors()),
            "request_id": rid,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    rid = _request_id(request)
    return JSONResponse(
        status_code=500,
        content={"error": err("internal_error", "Internal server error."), "request_id": rid},
    )
