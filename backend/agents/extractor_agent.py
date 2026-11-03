import logging
import time
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from agents.prompts import EXTRACTOR_PROMPT
from agents.vision_agent import AgentError
from config import Settings
from schemas.document_schemas import ExtractedInvoice
from utils.llm_factory import build_chat_model

logger = logging.getLogger("datanova.agents.extractor")


def run_extractor_agent(spatial_markdown: str, settings: Settings) -> ExtractedInvoice:
    """Transforms spatial transcription into structured ExtractedInvoice schema."""
    if not spatial_markdown or len(spatial_markdown.strip()) < 20:
        raise AgentError("extractor", "Spatial markdown is empty or invalid.", "AGENT_EXTRACTOR_FAILED")

    start_time = time.perf_counter()
    logger.info("Extractor agent starting analysis.")

    model = build_chat_model(
        provider=settings.LLM_PROVIDER_EXTRACTOR,
        model=settings.EXTRACTOR_MODEL,
        settings=settings,
        temperature=0.0,
    )

    try:
        structured_model = model.with_structured_output(ExtractedInvoice, method="json_schema")
    except Exception:
        structured_model = model.with_structured_output(ExtractedInvoice, method="function_calling")

    messages = [
        SystemMessage(content=EXTRACTOR_PROMPT),
        HumanMessage(content=spatial_markdown),
    ]

    try:
        result = structured_model.invoke(messages)
        if isinstance(result, ExtractedInvoice):
            invoice = result
        elif isinstance(result, dict):
            invoice = ExtractedInvoice.model_validate(result)
        else:
            raise ValueError(f"Unexpected extractor output type: {type(result)}")
    except ValidationError as val_err:
        logger.warning("Extractor validation failed, attempting repair pass: %s", str(val_err))
        repair_messages = [
            SystemMessage(content=EXTRACTOR_PROMPT),
            HumanMessage(content=spatial_markdown),
            HumanMessage(
                content=f"Your previous output violated the schema with error: {str(val_err)}. "
                "Fix all field types and values and return strictly valid data according to schema."
            ),
        ]
        try:
            repaired = structured_model.invoke(repair_messages)
            if isinstance(repaired, ExtractedInvoice):
                invoice = repaired
            elif isinstance(repaired, dict):
                invoice = ExtractedInvoice.model_validate(repaired)
            else:
                raise ValueError(f"Repair pass returned invalid type: {type(repaired)}")
        except Exception as repair_exc:
            raise AgentError(
                "extractor",
                f"Extractor schema validation failed after repair: {str(repair_exc)}",
                "AGENT_EXTRACTOR_FAILED",
            ) from repair_exc
    except Exception as exc:
        raise AgentError(
            "extractor",
            f"Extractor agent failed during invocation: {str(exc)}",
            "AGENT_EXTRACTOR_FAILED",
        ) from exc

    duration = time.perf_counter() - start_time
    logger.info("Extractor agent succeeded in %.2fs (vendor: '%s', invoice: '%s')", duration, invoice.vendor_name, invoice.invoice_number)
    return invoice
