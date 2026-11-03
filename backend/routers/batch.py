import asyncio
import json
import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from db.session import get_db
from schemas.batch import BatchCreateResponse, BatchStatusResponse, BatchSummaryResponse
from services.batch_worker import get_batch_worker

logger = logging.getLogger("datanova.routers.batch")
router = APIRouter(prefix="/api/v1/batch", tags=["Batch Processing"])


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_202_ACCEPTED)
async def submit_batch(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    settings = get_settings()
    if not settings.FEATURE_BATCH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Batch processing is disabled by feature flag",
        )

    if not files:
        raise HTTPException(status_code=400, detail="No files provided in batch upload")

    if len(files) > settings.MAX_BATCH_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size {len(files)} exceeds maximum allowable of {settings.MAX_BATCH_FILES}",
        )

    file_tuples = []
    for f in files:
        content = await f.read()
        file_tuples.append((f.filename or "unknown", content))
        await f.close()

    worker = get_batch_worker()
    batch_res = await worker.submit_batch(file_tuples)

    return {
        "batch_id": batch_res.batch_id,
        "total_files": len(file_tuples),
        "status": "processing",
        "created_at": batch_res.created_at,
        "message": f"Batch of {len(file_tuples)} documents queued for multi-agent extraction",
    }


@router.get("/{batch_id}", response_model=Dict[str, Any])
async def get_batch_status(
    batch_id: str,
) -> Dict[str, Any]:
    settings = get_settings()
    if not settings.FEATURE_BATCH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Batch processing is disabled",
        )

    worker = get_batch_worker()
    status_resp = worker.get_batch(batch_id)
    if not status_resp:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found")

    return status_resp.model_dump()


@router.get("/{batch_id}/events")
async def get_batch_events_stream(batch_id: str) -> StreamingResponse:
    settings = get_settings()
    if not settings.FEATURE_BATCH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Batch processing is disabled",
        )

    worker = get_batch_worker()
    event_queue = worker.subscribe(batch_id)

    async def event_generator():
        try:
            while True:
                data = await event_queue.get()
                if data is None:
                    break
                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            worker.unsubscribe(batch_id, event_queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{batch_id}/cancel", response_model=Dict[str, Any])
async def cancel_batch(
    batch_id: str,
) -> Dict[str, Any]:
    settings = get_settings()
    if not settings.FEATURE_BATCH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Batch processing is disabled",
        )

    worker = get_batch_worker()
    cancelled = worker.cancel_batch(batch_id)
    if not cancelled:
        raise HTTPException(
            status_code=400,
            detail="Could not cancel batch. It may have already finished or does not exist.",
        )

    return {"batch_id": batch_id, "status": "cancelled", "message": "Batch execution cancelled"}


@router.get("/{batch_id}/summary", response_model=Dict[str, Any])
async def get_batch_summary(
    batch_id: str,
) -> Dict[str, Any]:
    settings = get_settings()
    if not settings.FEATURE_BATCH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Batch processing is disabled",
        )

    worker = get_batch_worker()
    summary = worker.get_summary(batch_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found")

    return summary.model_dump()
