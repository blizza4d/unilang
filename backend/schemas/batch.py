from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

BatchItemStatus = Literal["queued", "processing", "completed", "failed", "cancelled"]


class BatchItemSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    filename: str
    status: BatchItemStatus
    document_id: str | None = None
    vendor_name: str = ""
    total_amount: float = 0.0
    currency: str = ""
    error_code: str | None = None
    overall_status: str | None = None


class BatchCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_id: str
    items: list[BatchItemSummary]
    created_at: str


class BatchStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_id: str
    total_files: int
    completed_count: int
    failed_count: int
    needs_review_count: int
    items: list[BatchItemSummary]


class BatchSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_id: str
    total_files: int
    totals_by_currency: dict[str, float] = Field(default_factory=dict)
    total_tax: float = 0.0
    math_failures_count: int = 0
    average_confidence: float = 1.0
