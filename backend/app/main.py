from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.domain.errors import (
    DocumentRequired,
    DomainError,
    InvalidDocument,
    InvalidTransition,
    NotFound,
    VersionConflict,
)
from app.routes import health, obligations

_STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFound: 404,
    InvalidTransition: 409,
    VersionConflict: 409,
    DocumentRequired: 422,
    InvalidDocument: 422,
}


def _error_body(error: DomainError) -> dict:
    return {"error": {"type": type(error).__name__, "message": str(error)}}


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.data.database import run_migrations

    run_migrations()
    yield


def create_app() -> FastAPI:
    from app.config import get_settings

    settings = get_settings()
    origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]

    app = FastAPI(
        title="Compliance Obligations Tracker", version="0.1.0", lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, error: DomainError) -> JSONResponse:
        status_code = _STATUS_BY_ERROR.get(type(error), 400)
        return JSONResponse(status_code=status_code, content=_error_body(error))

    app.include_router(health.router)
    app.include_router(obligations.router)
    return app


app = create_app()
