import asyncio
import hashlib
import json
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from agents.graph import aprocess_document, aprocess_document_v2, stream_document
from config import get_settings
from db.repository import create_document, find_by_hash
from db.session import get_session
from schemas.document_schemas import ErrorResponse, FinalDocumentResponse
from schemas.grounding import ExtendedDocumentResponse
from services.demo_pipeline import run_demo_pipeline
from utils.file_parsers import detect_mime, validate_size

router = APIRouter(prefix="/api/v1", tags=["Extraction"])
settings = get_settings()


@router.get("/capabilities")
async def get_capabilities() -> dict[str, object]:
    """Exposes supported feature flags and active model providers."""
    return {
        "server_version": "2.0.0",
        "version": "2.0.0",
        "streaming": settings.FEATURE_STREAMING,
        "grounding": settings.FEATURE_GROUNDING,
        "persistence": settings.FEATURE_PERSISTENCE,
        "history": settings.FEATURE_PERSISTENCE,
        "batch": settings.FEATURE_BATCH,
        "exports": settings.FEATURE_EXPORTS,
        "eval_harness": settings.FEATURE_EVAL,
        "demo_mode": settings.FEATURE_DEMO_MODE,
        "rate_limit": settings.FEATURE_RATE_LIMIT,
        "max_upload_mb": settings.MAX_UPLOAD_MB,
        "max_pdf_pages": settings.MAX_PDF_PAGES,
        "max_batch_files": settings.MAX_BATCH_FILES,
        "features": {
            "streaming": settings.FEATURE_STREAMING,
            "grounding": settings.FEATURE_GROUNDING,
            "persistence": settings.FEATURE_PERSISTENCE,
            "batch": settings.FEATURE_BATCH,
            "exports": settings.FEATURE_EXPORTS,
            "eval": settings.FEATURE_EVAL,
            "demo_mode": settings.FEATURE_DEMO_MODE,
        },
        "providers": {
            "vision": settings.LLM_PROVIDER_VISION,
            "extractor": settings.LLM_PROVIDER_EXTRACTOR,
            "judge": settings.LLM_PROVIDER_JUDGE,
        },
        "models": {
            "vision": settings.VISION_MODEL,
            "extractor": settings.EXTRACTOR_MODEL,
            "judge": settings.JUDGE_MODEL,
        },
    }



@router.post("/extract", response_model=FinalDocumentResponse)
async def extract_invoice_v1(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> FinalDocumentResponse:
    """Phase 1 backwards-compatible extraction endpoint."""
    try:
        file_bytes = await file.read()
    finally:
        await file.close()

    validate_size(file_bytes, settings.MAX_UPLOAD_MB)
    detect_mime(file_bytes)

    if settings.FEATURE_DEMO_MODE:
        demo_resp = await run_demo_pipeline(file_bytes, file.filename or "")
        return FinalDocumentResponse(
            extracted_data=demo_resp.extracted_data,
            validation_metrics=demo_resp.validation_metrics,
            overall_status=demo_resp.overall_status,
        )

    # Deduplication cache check if persistence is on
    sha = hashlib.sha256(file_bytes).hexdigest()
    if settings.FEATURE_PERSISTENCE:
        existing = await find_by_hash(session, sha)
        if existing:
            raw_dict = json.loads(existing.result_json)
            return FinalDocumentResponse.model_validate(raw_dict)

    import sys
    main_mod = sys.modules.get("main")
    fn = getattr(main_mod, "aprocess_document", aprocess_document)
    resp = await fn(file_bytes)


    if settings.FEATURE_PERSISTENCE:
        await create_document(
            session=session,
            filename=file.filename or "invoice.pdf",
            mime=detect_mime(file_bytes),
            size_bytes=len(file_bytes),
            sha256=sha,
            page_count=1,
            status=resp.overall_status,
            vendor_name=resp.extracted_data.vendor_name,
            invoice_number=resp.extracted_data.invoice_number,
            total_amount=resp.extracted_data.total_amount,
            currency=resp.extracted_data.currency,
            result_dict=resp.model_dump(),
        )

    return resp


@router.post("/extract/v2", response_model=ExtendedDocumentResponse)
async def extract_invoice_v2(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> ExtendedDocumentResponse:
    """Phase 2 extended extraction endpoint with spatial grounding & usage."""
    try:
        file_bytes = await file.read()
    finally:
        await file.close()

    validate_size(file_bytes, settings.MAX_UPLOAD_MB)
    detect_mime(file_bytes)

    if settings.FEATURE_DEMO_MODE:
        return await run_demo_pipeline(file_bytes, file.filename or "")

    sha = hashlib.sha256(file_bytes).hexdigest()
    if settings.FEATURE_PERSISTENCE:
        existing = await find_by_hash(session, sha)
        if existing:
            raw_dict = json.loads(existing.result_json)
            return ExtendedDocumentResponse.model_validate(raw_dict)

    resp = await aprocess_document_v2(file_bytes)

    if settings.FEATURE_PERSISTENCE:
        await create_document(
            session=session,
            filename=file.filename or "invoice.pdf",
            mime=detect_mime(file_bytes),
            size_bytes=len(file_bytes),
            sha256=sha,
            page_count=resp.page_count,
            status=resp.overall_status,
            vendor_name=resp.extracted_data.vendor_name,
            invoice_number=resp.extracted_data.invoice_number,
            total_amount=resp.extracted_data.total_amount,
            currency=resp.extracted_data.currency,
            result_dict=resp.model_dump(),
            grounding_dict=resp.grounding.model_dump() if resp.grounding else None,
            processing_ms=resp.processing_ms,
            usage_dict=resp.usage.model_dump() if resp.usage else None,
        )

    return resp


@router.post("/extract/stream")
async def extract_invoice_stream(
    request: Request,
    file: UploadFile = File(...),
) -> StreamingResponse:
    """Live Server-Sent Events stream delivering real-time per-agent status."""
    try:
        file_bytes = await file.read()
    finally:
        await file.close()

    validate_size(file_bytes, settings.MAX_UPLOAD_MB)
    detect_mime(file_bytes)

    def is_cancelled() -> bool:
        return asyncio.run_coroutine_threadsafe(
            request.is_disconnected(), asyncio.get_event_loop()
        ).result()

    async def sse_generator() -> AsyncGenerator[str, None]:
        if settings.FEATURE_DEMO_MODE:
            demo_resp = await run_demo_pipeline(file_bytes, file.filename or "")
            yield f"event: stage\ndata: {json.dumps({'stage': 'prepare', 'status': 'completed', 'duration_ms': 120, 'message': 'Prepared document'})}\n\n"
            await asyncio.sleep(0.5)
            yield f"event: stage\ndata: {json.dumps({'stage': 'vision', 'status': 'completed', 'duration_ms': 600, 'message': 'Spatial OCR transcription'})}\n\n"
            await asyncio.sleep(0.5)
            yield f"event: stage\ndata: {json.dumps({'stage': 'extractor', 'status': 'completed', 'duration_ms': 400, 'message': 'Structured business entities'})}\n\n"
            await asyncio.sleep(0.5)
            yield f"event: stage\ndata: {json.dumps({'stage': 'judge', 'status': 'completed', 'duration_ms': 350, 'message': 'Verified mathematical consistency'})}\n\n"
            yield f"event: result\ndata: {json.dumps({'result': demo_resp.model_dump(), 'document_id': None})}\n\n"
            return

        async for item in stream_document(
            file_bytes,
            request_id=getattr(request.state, "request_id", ""),
            is_cancelled_check=is_cancelled,
        ):
            if hasattr(item, "stage") and hasattr(item, "status"):
                yield f"event: stage\ndata: {item.model_dump_json()}\n\n"
            elif hasattr(item, "result"):
                yield f"event: result\ndata: {item.model_dump_json()}\n\n"
            elif hasattr(item, "error_code"):
                yield f"event: error\ndata: {item.model_dump_json()}\n\n"
            elif hasattr(item, "timestamp"):
                yield f"event: heartbeat\ndata: {item.model_dump_json()}\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
