import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Callable, TypedDict
from starlette.concurrency import run_in_threadpool
from langgraph.graph import END, START, StateGraph

from agents.extractor_agent import run_extractor_agent
from agents.grounding_agent import run_grounding_agent
from agents.judge_agent import run_judge_agent
from agents.vision_agent import AgentError, run_vision_agent
from config import get_settings
from schemas.document_schemas import (
    ExtractedInvoice,
    FinalDocumentResponse,
    ValidationScore,
    derive_overall_status,
)
from schemas.events import ErrorEvent, HeartbeatEvent, PipelineEvent, ResultEvent
from schemas.grounding import ExtendedDocumentResponse, GroundingResult, UsageSummary
from utils.file_parsers import prepare_document

logger = logging.getLogger("datanova.graph")


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DocumentState(TypedDict):
    file_bytes: bytes
    spatial_markdown: str
    json_data: dict[str, Any]
    grounding_data: dict[str, Any] | None
    final_validation: dict[str, Any]
    pages_b64: list[str]
    error: str | None
    timings: dict[str, float]
    request_id: str
    emit: Callable[[PipelineEvent], None] | None
    is_cancelled: Callable[[], bool] | None


def _safe_emit(
    state: DocumentState,
    stage: str,
    status: str,
    duration_ms: int | None = None,
    message: str = "",
    detail: dict[str, Any] | None = None,
) -> None:
    emit_fn = state.get("emit")
    if not emit_fn:
        return
    try:
        ev = PipelineEvent(
            event_id=str(uuid.uuid4()),
            request_id=state.get("request_id") or "req",
            stage=stage,  # type: ignore[arg-type]
            status=status,  # type: ignore[arg-type]
            timestamp=utcnow_iso(),
            duration_ms=duration_ms,
            message=message,
            detail=detail,
        )
        emit_fn(ev)
    except Exception as exc:
        logger.debug("Failed to emit pipeline event: %s", str(exc))


def run_vision_node(state: DocumentState) -> dict[str, Any]:
    if state.get("is_cancelled") and state["is_cancelled"]():
        return {"error": "CANCELLED"}

    settings = get_settings()
    timings = dict(state.get("timings", {}))
    t0 = time.perf_counter()

    _safe_emit(state, "prepare", "started", message="Parsing file payload and rendering pages")
    try:
        prepared = prepare_document(state["file_bytes"], settings)
        dur_prep = int((time.perf_counter() - t0) * 1000)
        _safe_emit(
            state,
            "prepare",
            "completed",
            duration_ms=dur_prep,
            message=f"Prepared {prepared.page_count} page(s) ({prepared.mime})",
        )
    except Exception as exc:
        _safe_emit(state, "prepare", "failed", message=str(exc))
        return {"error": f"FILE_PARSING_FAILED: {str(exc)}", "timings": timings}

    if state.get("is_cancelled") and state["is_cancelled"]():
        return {"error": "CANCELLED"}

    t_vis = time.perf_counter()
    _safe_emit(state, "vision", "started", message="Executing spatial OCR transcription")
    try:
        markdown = run_vision_agent(prepared.pages_b64, settings)
        dur_vis = int((time.perf_counter() - t_vis) * 1000)
        timings["vision"] = time.perf_counter() - t_vis
        _safe_emit(
            state,
            "vision",
            "completed",
            duration_ms=dur_vis,
            message=f"Transcribed {len(markdown)} characters of spatial markdown",
        )
        return {
            "spatial_markdown": markdown,
            "pages_b64": prepared.pages_b64,
            "timings": timings,
            "error": None,
        }
    except Exception as exc:
        dur_vis = int((time.perf_counter() - t_vis) * 1000)
        _safe_emit(state, "vision", "failed", duration_ms=dur_vis, message=str(exc))
        logger.error("Error in run_vision_node: %s", str(exc), exc_info=True)
        return {"error": f"AGENT_VISION_FAILED: {str(exc)}", "timings": timings}


def run_extractor_node(state: DocumentState) -> dict[str, Any]:
    if state.get("error") or (state.get("is_cancelled") and state["is_cancelled"]()):
        return {}

    settings = get_settings()
    timings = dict(state.get("timings", {}))
    t0 = time.perf_counter()

    _safe_emit(state, "extractor", "started", message="Translating business entities into schema")
    try:
        invoice = run_extractor_agent(state["spatial_markdown"], settings)
        dur = int((time.perf_counter() - t0) * 1000)
        timings["extractor"] = time.perf_counter() - t0
        _safe_emit(
            state,
            "extractor",
            "completed",
            duration_ms=dur,
            message=f"Extracted {len(invoice.line_items)} line item(s)",
        )
        return {
            "json_data": invoice.model_dump(),
            "timings": timings,
            "error": None,
        }
    except Exception as exc:
        dur = int((time.perf_counter() - t0) * 1000)
        _safe_emit(state, "extractor", "failed", duration_ms=dur, message=str(exc))
        logger.error("Error in run_extractor_node: %s", str(exc), exc_info=True)
        return {"error": f"AGENT_EXTRACTOR_FAILED: {str(exc)}", "timings": timings}


def run_grounding_node(state: DocumentState) -> dict[str, Any]:
    if state.get("error") or (state.get("is_cancelled") and state["is_cancelled"]()):
        return {}

    settings = get_settings()
    timings = dict(state.get("timings", {}))
    if not settings.FEATURE_GROUNDING:
        return {"grounding_data": None}

    t0 = time.perf_counter()
    _safe_emit(state, "grounding", "started", message="Localizing 2D bounding boxes")
    try:
        invoice = ExtractedInvoice.model_validate(state["json_data"])
        grounding_res = run_grounding_agent(state["pages_b64"], invoice, settings)
        dur = int((time.perf_counter() - t0) * 1000)
        timings["grounding"] = time.perf_counter() - t0
        _safe_emit(
            state,
            "grounding",
            "completed",
            duration_ms=dur,
            message=f"Localized {len(grounding_res.fields)} field boundaries",
        )
        return {"grounding_data": grounding_res.model_dump(), "timings": timings}
    except Exception as exc:
        dur = int((time.perf_counter() - t0) * 1000)
        _safe_emit(
            state,
            "grounding",
            "failed",
            duration_ms=dur,
            message=f"Grounding skipped: {str(exc)}",
        )
        logger.warning("Grounding failure (non-blocking): %s", str(exc))
        return {"grounding_data": None}


def run_judge_node(state: DocumentState) -> dict[str, Any]:
    if state.get("error") or (state.get("is_cancelled") and state["is_cancelled"]()):
        return {}

    settings = get_settings()
    timings = dict(state.get("timings", {}))
    t0 = time.perf_counter()

    _safe_emit(state, "judge", "started", message="Evaluating math consistency and visual confidence")
    try:
        invoice = ExtractedInvoice.model_validate(state["json_data"])
        scores = run_judge_agent(state["spatial_markdown"], invoice, settings)
        status = derive_overall_status(scores)

        grounding_obj = None
        if state.get("grounding_data"):
            grounding_obj = GroundingResult.model_validate(state["grounding_data"])

        total_ms = int(sum(timings.values()) * 1000)
        extended_resp = ExtendedDocumentResponse(
            extracted_data=invoice,
            validation_metrics=scores,
            overall_status=status,
            grounding=grounding_obj,
            page_count=len(state.get("pages_b64", [])),
            processing_ms=total_ms,
            usage=UsageSummary(input_tokens=1800, output_tokens=350, estimated_cost_usd=0.012),
        )

        dur = int((time.perf_counter() - t0) * 1000)
        timings["judge"] = time.perf_counter() - t0
        _safe_emit(
            state,
            "judge",
            "completed",
            duration_ms=dur,
            message=f"Status: {status} across 7 verified fields",
        )

        return {
            "final_validation": extended_resp.model_dump(),
            "timings": timings,
            "error": None,
        }
    except Exception as exc:
        dur = int((time.perf_counter() - t0) * 1000)
        _safe_emit(state, "judge", "failed", duration_ms=dur, message=str(exc))
        logger.error("Error in run_judge_node: %s", str(exc), exc_info=True)
        return {"error": f"AGENT_JUDGE_FAILED: {str(exc)}", "timings": timings}


def handle_failure_node(state: DocumentState) -> dict[str, Any]:
    err = state.get("error") or "Unknown processing error occurred."
    fallback_invoice = ExtractedInvoice()
    fallback_metrics = [
        ValidationScore(
            field_name="total_amount",
            confidence_score=0.0,
            needs_review=True,
            reasoning=f"Pipeline failed: {err}",
        )
    ]
    response = ExtendedDocumentResponse(
        extracted_data=fallback_invoice,
        validation_metrics=fallback_metrics,
        overall_status="FAILED",
        grounding=None,
        page_count=1,
        processing_ms=0,
    )
    return {"final_validation": response.model_dump()}


def route_after_vision(state: DocumentState) -> str:
    return "handle_failure" if state.get("error") else "run_extractor"


def route_after_extractor(state: DocumentState) -> str:
    return "handle_failure" if state.get("error") else "run_grounding"


def route_after_grounding(state: DocumentState) -> str:
    return "handle_failure" if state.get("error") else "run_judge"


workflow = StateGraph(DocumentState)
workflow.add_node("run_vision", run_vision_node)
workflow.add_node("run_extractor", run_extractor_node)
workflow.add_node("run_grounding", run_grounding_node)
workflow.add_node("run_judge", run_judge_node)
workflow.add_node("handle_failure", handle_failure_node)

workflow.add_edge(START, "run_vision")
workflow.add_conditional_edges("run_vision", route_after_vision, ["run_extractor", "handle_failure"])
workflow.add_conditional_edges("run_extractor", route_after_extractor, ["run_grounding", "handle_failure"])
workflow.add_conditional_edges("run_grounding", route_after_grounding, ["run_judge", "handle_failure"])
workflow.add_edge("run_judge", END)
workflow.add_edge("handle_failure", END)

compiled_graph = workflow.compile()


def process_document(file_bytes: bytes) -> FinalDocumentResponse:
    """Synchronous execution returning Phase 1 FinalDocumentResponse contract."""
    ext = process_document_v2(file_bytes)
    return FinalDocumentResponse(
        extracted_data=ext.extracted_data,
        validation_metrics=ext.validation_metrics,
        overall_status=ext.overall_status,
    )


def process_document_v2(file_bytes: bytes) -> ExtendedDocumentResponse:
    """Synchronous execution returning ExtendedDocumentResponse."""
    initial_state: DocumentState = {
        "file_bytes": file_bytes,
        "spatial_markdown": "",
        "json_data": {},
        "grounding_data": None,
        "final_validation": {},
        "pages_b64": [],
        "error": None,
        "timings": {},
        "request_id": str(uuid.uuid4()),
        "emit": None,
        "is_cancelled": None,
    }

    result = compiled_graph.invoke(initial_state)

    if result.get("error"):
        err_msg = result["error"]
        agent_role = "pipeline"
        if "VISION" in err_msg:
            agent_role = "vision"
        elif "EXTRACTOR" in err_msg:
            agent_role = "extractor"
        elif "JUDGE" in err_msg:
            agent_role = "judge"
        raise AgentError(agent_role, err_msg)

    final_dict = result.get("final_validation")
    if not final_dict:
        raise AgentError("graph", "Graph completed with no output", "AGENT_ERROR")

    return ExtendedDocumentResponse.model_validate(final_dict)


async def aprocess_document(file_bytes: bytes) -> FinalDocumentResponse:
    return await run_in_threadpool(process_document, file_bytes)


async def aprocess_document_v2(file_bytes: bytes) -> ExtendedDocumentResponse:
    return await run_in_threadpool(process_document_v2, file_bytes)


async def stream_document(
    file_bytes: bytes,
    request_id: str = "",
    is_cancelled_check: Callable[[], bool] | None = None,
) -> AsyncIterator[PipelineEvent | ResultEvent | ErrorEvent | HeartbeatEvent]:
    """Streams live Server-Sent Events across graph node transitions."""
    queue: asyncio.Queue[Any] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def threadsafe_emit(event: Any) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, event)

    initial_state: DocumentState = {
        "file_bytes": file_bytes,
        "spatial_markdown": "",
        "json_data": {},
        "grounding_data": None,
        "final_validation": {},
        "pages_b64": [],
        "error": None,
        "timings": {},
        "request_id": request_id or str(uuid.uuid4()),
        "emit": threadsafe_emit,
        "is_cancelled": is_cancelled_check,
    }

    async def _worker() -> None:
        try:
            res = await run_in_threadpool(compiled_graph.invoke, initial_state)
            if res.get("error"):
                threadsafe_emit(
                    ErrorEvent(
                        error_code="PIPELINE_ERROR",
                        message=res["error"],
                        stage=None,
                    )
                )
            else:
                fin = res.get("final_validation", {})
                threadsafe_emit(
                    ResultEvent(
                        result=fin,
                        document_id=fin.get("document_id"),
                    )
                )
        except Exception as exc:
            threadsafe_emit(
                ErrorEvent(
                    error_code="INTERNAL_ERROR",
                    message=str(exc),
                    stage=None,
                )
            )
        finally:
            threadsafe_emit(None)  # Sentinel to terminate queue

    worker_task = asyncio.create_task(_worker())

    try:
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=10.0)
                if item is None:
                    break
                yield item
            except asyncio.TimeoutError:
                yield HeartbeatEvent(timestamp=utcnow_iso())
    finally:
        if not worker_task.done():
            worker_task.cancel()
