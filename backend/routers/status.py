import os
import shutil
import time
from datetime import datetime, timezone
from fastapi import APIRouter
from config import get_settings

router = APIRouter(tags=["Status"])
START_TIME = time.time()


@router.get("/status")
async def get_system_status() -> dict:
    settings = get_settings()
    uptime_seconds = int(time.time() - START_TIME)

    # Check Poppler utilities
    poppler_available = bool(shutil.which("pdftoppm") or shutil.which("pdfinfo"))

    # Check LLM Provider Keys
    has_openai = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())
    has_google = bool(settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY.strip())

    demo_reason = "explicitly_enabled" if settings.FEATURE_DEMO_MODE else (
        "no_api_keys_configured" if not (has_openai or has_google) else "live_ai_active"
    )

    return {
        "service": "DataNova Extract API",
        "version": "1.0.0-rc.1",
        "commit_sha": os.getenv("VERCEL_GIT_COMMIT_SHA") or os.getenv("GIT_COMMIT_SHA") or "dev-local",
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": uptime_seconds,
        "demo_mode": {
            "active": settings.FEATURE_DEMO_MODE or not (has_openai or has_google),
            "reason": demo_reason,
        },
        "providers": {
            "openai_configured": has_openai,
            "google_configured": has_google,
            "vision_model": settings.VISION_MODEL,
            "extractor_model": settings.EXTRACTOR_MODEL,
        },
        "system": {
            "poppler_installed": poppler_available,
            "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
            "daily_budget_usd": settings.DAILY_BUDGET_USD,
            "database_configured": bool(settings.DATABASE_URL),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
