import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from db.session import get_db
from db.repository import DocumentRepository

logger = logging.getLogger("datanova.routers.documents")
router = APIRouter(prefix="/api/v1/documents", tags=["Persistence & History"])


class PatchDocumentPayload(BaseModel):
    user_id: str = "operator"
    reason: Optional[str] = "Manual correction"
    fields: Dict[str, Any] = Field(
        ..., description="Key-value mapping of fields to update in extracted data"
    )


class ApproveDocumentPayload(BaseModel):
    user_id: str = "reviewer"
    notes: Optional[str] = None


@router.get("", response_model=Dict[str, Any])
async def list_documents(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    settings = get_settings()
    if not settings.FEATURE_HISTORY:
        return {"items": [], "total": 0, "message": "History persistence is disabled"}

    repo = DocumentRepository(db)
    items = await repo.list_documents(limit=limit, offset=offset)
    return {
        "items": [item.to_dict() for item in items],
        "limit": limit,
        "offset": offset,
        "count": len(items),
    }


@router.get("/{document_id}", response_model=Dict[str, Any])
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    settings = get_settings()
    if not settings.FEATURE_HISTORY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History persistence feature is disabled",
        )

    repo = DocumentRepository(db)
    doc = await repo.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found",
        )
    return doc.to_dict()


@router.patch("/{document_id}", response_model=Dict[str, Any])
async def patch_document(
    document_id: str,
    payload: PatchDocumentPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    settings = get_settings()
    if not settings.FEATURE_HISTORY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="History edits are disabled by feature flag",
        )

    repo = DocumentRepository(db)
    doc = await repo.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found",
        )

    updated_doc = await repo.record_field_edits(
        document_id=document_id,
        user_id=payload.user_id,
        field_updates=payload.fields,
        reason=payload.reason,
    )
    if not updated_doc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply document field updates",
        )

    return updated_doc.to_dict()


@router.post("/{document_id}/approve", response_model=Dict[str, Any])
async def approve_document(
    document_id: str,
    payload: ApproveDocumentPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    settings = get_settings()
    if not settings.FEATURE_HISTORY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="History features are disabled by feature flag",
        )

    repo = DocumentRepository(db)
    doc = await repo.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found",
        )

    updated_doc = await repo.record_approval(
        document_id=document_id,
        user_id=payload.user_id,
        notes=payload.notes,
    )
    if not updated_doc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record document approval",
        )

    return updated_doc.to_dict()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    settings = get_settings()
    if not settings.FEATURE_HISTORY:
        return

    repo = DocumentRepository(db)
    deleted = await repo.delete_document(document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found",
        )
