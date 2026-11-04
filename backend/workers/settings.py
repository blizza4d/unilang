from typing import Any
from arq.connections import RedisSettings
from config import get_settings

settings = get_settings()


def get_redis_settings() -> RedisSettings:
    """Parse application REDIS_URL into arq RedisSettings."""
    raw_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
    return RedisSettings.from_dsn(raw_url)


class WorkerSettings:
    """Arq worker configuration."""
    from workers.tasks import (
        deliver_webhook_task,
        export_task,
        ingest_email_task,
        process_batch_item_task,
        process_document_task,
    )

    functions = [
        process_document_task,
        process_batch_item_task,
        deliver_webhook_task,
        export_task,
        ingest_email_task,
    ]
    redis_settings = get_redis_settings()
    max_tries = getattr(settings, "JOB_MAX_TRIES", 3)
    job_timeout = getattr(settings, "JOB_TIMEOUT_SECONDS", 300)
    max_jobs = getattr(settings, "WORKER_CONCURRENCY", 10)
