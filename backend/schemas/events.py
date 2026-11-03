from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

PipelineStage = Literal[
    "prepare", "vision", "extractor", "grounding", "judge", "finalize"
]
StageStatus = Literal["started", "completed", "failed"]


class PipelineEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    request_id: str
    stage: PipelineStage
    status: StageStatus
    timestamp: str
    duration_ms: int | None = None
    message: str
    detail: dict[str, Any] | None = None


class ResultEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    result: dict[str, Any]
    document_id: str | None = None


class ErrorEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error_code: str
    message: str
    stage: PipelineStage | None = None


class HeartbeatEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: str
