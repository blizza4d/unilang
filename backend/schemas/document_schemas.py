import re
from datetime import date as dt_date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

INVOICE_FIELD_NAMES: tuple[str, ...] = (
    "vendor_name",
    "invoice_number",
    "date",
    "currency",
    "total_amount",
    "tax_amount",
    "line_items",
)


class LineItem(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    description: str = ""
    quantity: float = 0.0
    unit_price: float = 0.0
    total_price: float = 0.0


class ExtractedInvoice(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    vendor_name: str = ""
    invoice_number: str = ""
    date: str = ""
    currency: str = ""
    total_amount: float = 0.0
    tax_amount: float = 0.0
    line_items: list[LineItem] = Field(default_factory=list)

    @field_validator("currency", mode="before")
    @classmethod
    def validate_currency(cls, value: object) -> str:
        if not isinstance(value, str):
            return ""
        cleaned = value.strip().upper()
        if len(cleaned) == 3 and cleaned.isalpha():
            return cleaned
        return ""

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, value: object) -> str:
        if not isinstance(value, str):
            return ""
        val = value.strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", val):
            return ""
        try:
            dt_date.fromisoformat(val)
            return val
        except ValueError:
            return ""


class ValidationScore(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    field_name: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    needs_review: bool
    reasoning: str

    @field_validator("field_name")
    @classmethod
    def validate_field_name(cls, value: str) -> str:
        if value not in INVOICE_FIELD_NAMES:
            raise ValueError(
                f"field_name '{value}' must be one of {INVOICE_FIELD_NAMES}"
            )
        return value


class FinalDocumentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    extracted_data: ExtractedInvoice
    validation_metrics: list[ValidationScore]
    overall_status: Literal["APPROVED", "REQUIRES_HUMAN_REVIEW", "FAILED"]


def derive_overall_status(
    metrics: list[ValidationScore],
) -> Literal["APPROVED", "REQUIRES_HUMAN_REVIEW", "FAILED"]:
    if not metrics:
        return "FAILED"
    if any(metric.needs_review for metric in metrics):
        return "REQUIRES_HUMAN_REVIEW"
    return "APPROVED"


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    error_code: str
    message: str
    request_id: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: str
    version: str
