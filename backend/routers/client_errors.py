import logging
from typing import Optional
from fastapi import APIRouter, Request, status
from pydantic import BaseModel, Field

logger = logging.getLogger("datanova.client_errors")
router = APIRouter(prefix="/api/v1", tags=["Client Errors"])


class ClientErrorPayload(BaseModel):
    message: str = Field(max_length=500)
    source: Optional[str] = Field(default=None, max_length=200)
    lineno: Optional[int] = None
    colno: Optional[int] = None
    url: Optional[str] = Field(default=None, max_length=500)
    user_agent: Optional[str] = Field(default=None, max_length=300)
    app_version: Optional[str] = Field(default=None, max_length=50)


@router.post("/client-errors", status_code=status.HTTP_204_NO_CONTENT)
async def log_client_error(payload: ClientErrorPayload, request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    logger.warning(
        "Client-side frontend error reported: %s (source: %s:%s, ip: %s)",
        payload.message,
        payload.source,
        payload.lineno,
        ip,
    )
    return None
