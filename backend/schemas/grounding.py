from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from schemas.document_schemas import ExtractedInvoice, FinalDocumentResponse, ValidationScore


class BoundingBox(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(ge=1, default=1)
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)
    width: float = Field(ge=0.0, le=1.0)
    height: float = Field(ge=0.0, le=1.0)


class FieldGrounding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_name: str
    boxes: list[BoundingBox] = Field(default_factory=list)
    source_text: str = ""
    grounding_confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class LineItemGrounding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    row_index: int
    prop: Literal["description", "quantity", "unit_price", "total_price"]
    box: BoundingBox | None = None


class PageDimension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(ge=1, default=1)
    width_px: int = 1000
    height_px: int = 1414


class GroundingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fields: list[FieldGrounding] = Field(default_factory=list)
    line_items: list[LineItemGrounding] = Field(default_factory=list)
    page_dimensions: list[PageDimension] = Field(default_factory=list)


class UsageSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float | None = None


class ExtendedDocumentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    extracted_data: ExtractedInvoice
    validation_metrics: list[ValidationScore]
    overall_status: Literal["APPROVED", "REQUIRES_HUMAN_REVIEW", "FAILED"]
    grounding: GroundingResult | None = None
    document_id: str | None = None
    page_count: int = 1
    processing_ms: int = 0
    usage: UsageSummary | None = None
    source: str | None = None
    is_demo: bool = False
