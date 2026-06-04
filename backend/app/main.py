from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.deps import (
    get_diagnosis_service,
    get_knowledge_base_service,
    get_upload_service,
)
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError, NotFoundError, ValidationError


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    get_upload_service().ensure_ready()
    get_knowledge_base_service().ensure_ready()
    get_diagnosis_service().ensure_ready()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api/v1")

    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        _request: Request, exc: ValidationError
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(
        _request: Request, exc: NotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": exc.message})

    return app


app = create_app()
