import asyncio
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
import sys
from typing import AsyncGenerator

# Ensure backend directory is on sys.path regardless of execution working directory
_backend_dir = str(Path(__file__).resolve().parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config import get_settings
from db.session import init_db
from middleware.budget_limit import BudgetLimitMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.request_context import RequestContextMiddleware
from middleware.security_headers import SecurityHeadersMiddleware
from routers import batch, client_errors as client_errors_router, documents, eval as eval_router, exports, extract, health, status as status_router, v3_extract
from schemas.document_schemas import ErrorResponse
from utils.file_parsers import (
    CorruptFileError,
    EmptyFileError,
    FileParsingError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)
from utils.logging_setup import setup_logging
from agents.vision_agent import AgentError
from agents.graph import aprocess_document


settings = get_settings()
setup_logging(log_level=settings.LOG_LEVEL, json_format=settings.JSON_LOGS)
logger = logging.getLogger("datanova.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Initializing DataNova Extract Server (Phase 2)...")
    if settings.FEATURE_HISTORY or settings.FEATURE_BATCH:
        logger.info("Initializing persistence database engine...")
        await init_db()
    yield
    logger.info("DataNova Extract Server shutting down cleanly.")


app = FastAPI(
    title="DataNova Extract API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 1. Context & Trace Middleware
app.add_middleware(RequestContextMiddleware)

# 2. Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2.5 Spend Caps & Budget Fallback Middleware
app.add_middleware(BudgetLimitMiddleware)

# 3. Rate Limit Middleware
if settings.FEATURE_RATE_LIMIT:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    )

# 4. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://uni-lang.vercel.app",
    ],
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_req_id(request: Request) -> str:
    return getattr(request.state, "request_id", "req-unknown")


# Exception Handlers
@app.exception_handler(EmptyFileError)
async def empty_file_handler(request: Request, exc: EmptyFileError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error_code="EMPTY_FILE",
            message=str(exc) or "The uploaded document is empty.",
            request_id=_get_req_id(request),
        ).model_dump(),
    )


@app.exception_handler(CorruptFileError)
async def corrupt_file_handler(request: Request, exc: CorruptFileError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error_code="CORRUPT_FILE",
            message="We couldn't read that file. Try another copy.",
            request_id=_get_req_id(request),
        ).model_dump(),
    )


@app.exception_handler(FileTooLargeError)
async def file_too_large_handler(request: Request, exc: FileTooLargeError) -> JSONResponse:
    return JSONResponse(
        status_code=413,
        content=ErrorResponse(
            error_code="FILE_TOO_LARGE",
            message=f"File exceeds the {settings.MAX_UPLOAD_MB} MB limit.",
            request_id=_get_req_id(request),
        ).model_dump(),
    )


@app.exception_handler(UnsupportedFileTypeError)
async def unsupported_type_handler(request: Request, exc: UnsupportedFileTypeError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        content=ErrorResponse(
            error_code="UNSUPPORTED_TYPE",
            message="Unsupported file type. Please upload a PDF, PNG, JPG, or WEBP document.",
            request_id=_get_req_id(request),
        ).model_dump(),
    )


@app.exception_handler(FileParsingError)
async def general_parsing_handler(request: Request, exc: FileParsingError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error_code="CORRUPT_FILE",
            message=str(exc),
            request_id=_get_req_id(request),
        ).model_dump(),
    )


@app.exception_handler(AgentError)
async def agent_error_handler(request: Request, exc: AgentError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error_code=exc.error_code or "AGENT_FAILED",
            message="Document processing agent encountered an error. Please retry.",
            request_id=_get_req_id(request),
        ).model_dump(),
    )


@app.exception_handler(asyncio.TimeoutError)
async def timeout_handler(request: Request, exc: asyncio.TimeoutError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content=ErrorResponse(
            error_code="UPSTREAM_TIMEOUT",
            message="The AI processing pipeline took too long. Please retry.",
            request_id=_get_req_id(request),
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Invalid request format.",
            request_id=_get_req_id(request),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled server exception: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="Something went wrong on our side.",
            request_id=_get_req_id(request),
        ).model_dump(),
    )


# Mount All Feature Routers
app.include_router(extract.router)
app.include_router(documents.router)
app.include_router(batch.router)
app.include_router(exports.router)
app.include_router(eval_router.router)
app.include_router(health.router)
app.include_router(status_router.router)
app.include_router(client_errors_router.router)
app.include_router(v3_extract.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
