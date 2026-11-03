import logging
import time
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, ConfigDict, Field

from agents.prompts import GROUNDING_PROMPT
from config import Settings
from schemas.document_schemas import ExtractedInvoice
from schemas.grounding import (
    BoundingBox,
    FieldGrounding,
    GroundingResult,
    LineItemGrounding,
    PageDimension,
)
from utils.llm_factory import build_chat_model, build_image_message

logger = logging.getLogger("datanova.agents.grounding")


class RawBox(BaseModel):
    model_config = ConfigDict(extra="ignore")
    page: int = 1
    x: float
    y: float
    width: float
    height: float


class RawFieldGrounding(BaseModel):
    model_config = ConfigDict(extra="ignore")
    field_name: str
    boxes: list[RawBox] = Field(default_factory=list)
    source_text: str = ""


class RawGroundingOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    fields: list[RawFieldGrounding] = Field(default_factory=list)


def _sanitize_box(raw: RawBox, max_page: int) -> BoundingBox | None:
    if raw.page < 1 or raw.page > max_page:
        return None

    # Clamp coordinates to [0.0, 1.0]
    x = max(0.0, min(1.0, float(raw.x)))
    y = max(0.0, min(1.0, float(raw.y)))
    w = max(0.0, min(1.0 - x, float(raw.width)))
    h = max(0.0, min(1.0 - y, float(raw.height)))

    # Reject degenerate or oversized boxes (> 40% page area)
    area = w * h
    if area <= 0.0001 or area > 0.40:
        return None

    return BoundingBox(page=raw.page, x=x, y=y, width=w, height=h)


def sanitize_box_coords(box: list[int | float]) -> list[int]:
    """Sanitizes normalized integer bounding boxes in [0, 1000] space [ymin, xmin, ymax, xmax]."""
    ymin, xmin, ymax, xmax = box
    ymin = max(0, min(1000, int(ymin)))
    xmin = max(0, min(1000, int(xmin)))
    ymax = max(0, min(1000, int(ymax)))
    xmax = max(0, min(1000, int(xmax)))
    if ymin > ymax:
        ymin, ymax = ymax, ymin
    if xmin > xmax:
        xmin, xmax = xmax, xmin
    return [ymin, xmin, ymax, xmax]



def run_grounding_agent(
    pages_b64: list[str],
    invoice: ExtractedInvoice,
    settings: Settings,
) -> GroundingResult:
    """Localizes extracted entities to 2D bounding boxes on document pages."""
    start_time = time.perf_counter()
    num_pages = len(pages_b64)
    logger.info("Grounding agent localizing fields across %d pages.", num_pages)

    dimensions = [
        PageDimension(page=i + 1, width_px=1000, height_px=1414)
        for i in range(num_pages)
    ]

    model = build_chat_model(
        provider=settings.LLM_PROVIDER_VISION,
        model=settings.VISION_MODEL,
        settings=settings,
        temperature=0.0,
    )

    try:
        structured_model = model.with_structured_output(
            RawGroundingOutput, method="json_schema"
        )
    except Exception:
        structured_model = model.with_structured_output(
            RawGroundingOutput, method="function_calling"
        )

    prompt_payload = (
        "Locate bounding boxes for the following extracted invoice data:\n"
        f"{invoice.model_dump_json(indent=2)}\n"
        "Return tight normalized coordinates [0.0 to 1.0] for visible values."
    )

    messages = [
        SystemMessage(content=GROUNDING_PROMPT),
        build_image_message(prompt_payload, pages_b64),
    ]

    field_groundings: list[FieldGrounding] = []
    line_groundings: list[LineItemGrounding] = []

    try:
        raw_result = structured_model.invoke(messages)
        if isinstance(raw_result, RawGroundingOutput):
            raw_fields = raw_result.fields
        elif isinstance(raw_result, dict) and "fields" in raw_result:
            raw_fields = [
                RawFieldGrounding.model_validate(f) for f in raw_result["fields"]
            ]
        else:
            raw_fields = []

        for rf in raw_fields:
            clean_boxes: list[BoundingBox] = []
            for b in rf.boxes:
                s_box = _sanitize_box(b, num_pages)
                if s_box:
                    clean_boxes.append(s_box)

            if clean_boxes:
                field_groundings.append(
                    FieldGrounding(
                        field_name=rf.field_name,
                        boxes=clean_boxes,
                        source_text=rf.source_text,
                        grounding_confidence=0.95,
                    )
                )
    except Exception as exc:
        logger.warning("Grounding LLM invocation failed: %s. Proceeding without boxes.", str(exc))

    duration = time.perf_counter() - start_time
    logger.info("Grounding completed in %.2fs with %d localized fields.", duration, len(field_groundings))

    return GroundingResult(
        fields=field_groundings,
        line_items=line_groundings,
        page_dimensions=dimensions,
    )
