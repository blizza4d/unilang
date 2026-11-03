import logging
from typing import Any, Dict, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
import io
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from db.session import get_db
from db.repository import DocumentRepository
from schemas.document_schemas import ExtractedInvoice, FinalDocumentResponse
from services.exporters import (
    export_json_bytes,
    export_csv_bytes,
    export_xlsx_bytes,
    export_pdf_bytes,
)

logger = logging.getLogger("datanova.routers.exports")
router = APIRouter(prefix="/api/v1", tags=["Export Suite"])

ExportFormat = Literal["json", "csv", "xlsx", "pdf"]


def _build_streaming_response(
    data_bytes: bytes,
    filename_base: str,
    export_format: ExportFormat,
) -> Response:
    media_types = {
        "json": "application/json",
        "csv": "text/csv; charset=utf-8",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf",
    }
    extensions = {
        "json": "json",
        "csv": "csv",
        "xlsx": "xlsx",
        "pdf": "pdf",
    }

    media_type = media_types[export_format]
    ext = extensions[export_format]
    filename = f"{filename_base}.{ext}"

    return StreamingResponse(
        io.BytesIO(data_bytes),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@router.get("/documents/{document_id}/export")
async def export_document_by_id(
    document_id: str,
    format: ExportFormat = Query("json", description="Export file format: json, csv, xlsx, pdf"),
    db: AsyncSession = Depends(get_db),
) -> Response:
    settings = get_settings()
    if not settings.FEATURE_EXPORTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Export suite is disabled by feature flag",
        )

    repo = DocumentRepository(db)
    doc = await repo.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found",
        )

    doc_dict = doc.to_dict()
    extracted_data = doc_dict.get("extracted_data")
    if not extracted_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Document has no extracted data to export",
        )

    filename_base = doc.filename.rsplit(".", 1)[0] if doc.filename else "datanova_export"

    if format == "json":
        data_bytes = export_json_bytes(extracted_data)
    elif format == "csv":
        data_bytes = export_csv_bytes(extracted_data)
    elif format == "xlsx":
        data_bytes = export_xlsx_bytes(extracted_data)
    elif format == "pdf":
        data_bytes = export_pdf_bytes(extracted_data, doc.filename)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{format}'")

    return _build_streaming_response(data_bytes, filename_base, format)


@router.post("/export/direct")
async def export_direct(
    payload: Dict[str, Any],
    format: ExportFormat = Query("json", description="Export file format: json, csv, xlsx, pdf"),
    filename: Optional[str] = Query("invoice", description="Base filename without extension"),
) -> Response:
    settings = get_settings()
    if not settings.FEATURE_EXPORTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Export suite is disabled by feature flag",
        )

    data_dict = payload

    filename_base = (filename or "invoice").rsplit(".", 1)[0]

    if format == "json":
        data_bytes = export_json_bytes(data_dict)
    elif format == "csv":
        data_bytes = export_csv_bytes(data_dict)
    elif format == "xlsx":
        data_bytes = export_xlsx_bytes(data_dict)
    elif format == "pdf":
        data_bytes = export_pdf_bytes(data_dict, filename_base)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{format}'")

    return _build_streaming_response(data_bytes, filename_base, format)
