import logging
import time
from typing import Any, Dict
from sqlalchemy import text
from db.session import engine

logger = logging.getLogger("datanova.db.health")


async def check_database_health() -> Dict[str, Any]:
    """Check database connectivity and reporting current migration revision."""
    start_time = time.perf_counter()
    status = "healthy"
    current_revision = "unknown"
    error_message = None

    try:
        async with engine.connect() as conn:
            # 1. Connectivity test
            await conn.execute(text("SELECT 1"))

            # 2. Alembic revision check
            try:
                result = await conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
                row = result.fetchone()
                if row:
                    current_revision = str(row[0])
                else:
                    current_revision = "none"
            except Exception:
                # alembic_version table may not exist yet in unmigrated test DBs
                current_revision = "uninitialized"

    except Exception as exc:
        status = "unhealthy"
        error_message = str(exc)
        logger.error("Database health check failed: %s", error_message)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "status": status,
        "database": engine.dialect.name,
        "current_revision": current_revision,
        "latency_ms": latency_ms,
        "error": error_message,
    }
