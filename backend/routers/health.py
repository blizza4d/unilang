import logging
import time
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from db.session import get_db

logger = logging.getLogger("datanova.routers.health")
router = APIRouter(tags=["Observability & Health"])

SERVER_START_TIME = time.time()


@router.get("/health", response_model=Dict[str, Any])
async def health_liveness() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "datanova-extract",
        "version": "2.0.0",
        "uptime_seconds": round(time.time() - SERVER_START_TIME, 1),
    }


@router.get("/health/deep", response_model=Dict[str, Any])
async def health_readiness(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    settings = get_settings()
    checks: Dict[str, Any] = {
        "database": False,
        "vision_provider": False,
        "extractor_provider": False,
        "judge_provider": False,
    }

    # 1. Database check
    if settings.FEATURE_HISTORY:
        try:
            await db.execute(text("SELECT 1"))
            checks["database"] = True
        except Exception as e:
            logger.error(f"Deep health check failed on DB: {e}")
            checks["database"] = False
    else:
        checks["database"] = "disabled_by_feature_flag"

    # 2. Key checks
    checks["vision_provider"] = bool(
        settings.GOOGLE_API_KEY
        if settings.LLM_PROVIDER_VISION == "google"
        else settings.OPENAI_API_KEY
    ) or settings.FEATURE_DEMO_MODE

    checks["extractor_provider"] = bool(
        settings.GOOGLE_API_KEY
        if settings.LLM_PROVIDER_EXTRACTOR == "google"
        else settings.OPENAI_API_KEY
    ) or settings.FEATURE_DEMO_MODE

    checks["judge_provider"] = bool(
        settings.GOOGLE_API_KEY
        if settings.LLM_PROVIDER_JUDGE == "google"
        else settings.OPENAI_API_KEY
    ) or settings.FEATURE_DEMO_MODE

    all_ready = all(
        v is True or v == "disabled_by_feature_flag" for v in checks.values()
    )

    if not all_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "degraded", "checks": checks},
        )

    return {
        "status": "ready",
        "checks": checks,
        "uptime_seconds": round(time.time() - SERVER_START_TIME, 1),
    }


@router.get("/metrics")
async def prometheus_metrics() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
