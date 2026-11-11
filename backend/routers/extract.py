import asyncio
import hashlib
import json
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
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


def should_use_demo_mode(request: Request | None, settings: object) -> tuple[bool, str]:
    if getattr(settings, "FEATURE_DEMO_MODE", False):
        return True, "explicit_demo_flag"
    has_openai = bool(getattr(settings, "OPENAI_API_KEY", "") and settings.OPENAI_API_KEY.strip())
    has_google = bool(getattr(settings, "GOOGLE_API_KEY", "") and settings.GOOGLE_API_KEY.strip())
    if not has_openai and not has_google:
        return True, "no_keys_configured"
    if request:
        req_state = getattr(request, "state", None)
        if getattr(req_state, "budget_exceeded", False):
            return True, "budget_cap_exceeded"
        live_code = getattr(settings, "LIVE_ACCESS_CODE", "")
        if live_code and live_code.strip():
            provided = request.headers.get("X-Live-Access-Code", "")
            if provided != live_code.strip():
                return True, "access_code_required"
    return False, "live_ai"


@router.get("/capabilities")
async def get_capabilities() -> dict[str, object]:
    """Exposes supported feature flags and active model providers."""
    settings = get_settings()
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
    request: Request,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> FinalDocumentResponse:
    """Phase 1 backwards-compatible extraction endpoint."""
    settings = get_settings()
    try:
        file_bytes = await file.read()
    finally:
        await file.close()

    validate_size(file_bytes, settings.MAX_UPLOAD_MB)
    detect_mime(file_bytes)

    use_demo, reason = should_use_demo_mode(request, settings)
    if use_demo:
        demo_resp = await run_demo_pipeline(file_bytes, file.filename or "")
        return FinalDocumentResponse(
            extracted_data=demo_resp.extracted_data,
            validation_metrics=demo_resp.validation_metrics,
            overall_status=demo_resp.overall_status,
            source="demo_fixture",
            is_demo=True,
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
    resp.source = "live_llm"
    resp.is_demo = False

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
    request: Request,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> ExtendedDocumentResponse:
    """Phase 2 extended extraction endpoint with spatial grounding & usage."""
    settings = get_settings()
    try:
        file_bytes = await file.read()
    finally:
        await file.close()

    validate_size(file_bytes, settings.MAX_UPLOAD_MB)
    detect_mime(file_bytes)

    use_demo, reason = should_use_demo_mode(request, settings)
    if use_demo:
        demo_resp = await run_demo_pipeline(file_bytes, file.filename or "")
        demo_resp.source = "demo_fixture"
        demo_resp.is_demo = True
        return demo_resp

    sha = hashlib.sha256(file_bytes).hexdigest()
    if settings.FEATURE_PERSISTENCE:
        existing = await find_by_hash(session, sha)
        if existing:
            raw_dict = json.loads(existing.result_json)
            return ExtendedDocumentResponse.model_validate(raw_dict)

    resp = await aprocess_document_v2(file_bytes)
    resp.source = "live_llm"
    resp.is_demo = False

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
    settings = get_settings()
    try:
        file_bytes = await file.read()
    finally:
        await file.close()

    validate_size(file_bytes, settings.MAX_UPLOAD_MB)
    detect_mime(file_bytes)

    loop = asyncio.get_running_loop()

    def is_cancelled() -> bool:
        try:
            future = asyncio.run_coroutine_threadsafe(request.is_disconnected(), loop)
            return future.result(timeout=0.05)
        except Exception:
            return False

    use_demo, reason = should_use_demo_mode(request, settings)

    async def sse_generator() -> AsyncGenerator[str, None]:
        if use_demo:
            demo_resp = await run_demo_pipeline(file_bytes, file.filename or "")
            demo_resp.source = "demo_fixture"
            demo_resp.is_demo = True
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
                if hasattr(item.result, "source"):
                    item.result.source = "live_llm"
                    item.result.is_demo = False
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
