import json
import logging
from typing import Any
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from db.models import ApprovalRecord, DocumentRecord, EditRecord, PageImageRecord

logger = logging.getLogger("datanova.repository")
settings = get_settings()


async def find_by_hash(session: AsyncSession, sha256_hash: str) -> DocumentRecord | None:
    stmt = select(DocumentRecord).where(DocumentRecord.sha256 == sha256_hash)
    res = await session.execute(stmt)
    return res.scalars().first()


async def get_document(session: AsyncSession, document_id: str) -> DocumentRecord | None:
    stmt = select(DocumentRecord).where(DocumentRecord.id == document_id)
    res = await session.execute(stmt)
    return res.scalars().first()


async def list_documents(
    session: AsyncSession,
    limit: int = 50,
    cursor: str | None = None,
    status: str | None = None,
    q: str | None = None,
) -> list[DocumentRecord]:
    stmt = select(DocumentRecord).order_by(desc(DocumentRecord.created_at))

    if status:
        stmt = stmt.where(DocumentRecord.status == status)
    if q:
        stmt = stmt.where(
            (DocumentRecord.vendor_name.ilike(f"%{q}%"))
            | (DocumentRecord.invoice_number.ilike(f"%{q}%"))
            | (DocumentRecord.filename.ilike(f"%{q}%"))
        )
    stmt = stmt.limit(limit)

    res = await session.execute(stmt)
    return list(res.scalars().all())


async def enforce_history_cap(session: AsyncSession) -> None:
    """Enforces MAX_HISTORY_ITEMS by trimming oldest documents."""
    count_stmt = select(func.count(DocumentRecord.id))
    total_count = (await session.execute(count_stmt)).scalar() or 0

    if total_count > settings.MAX_HISTORY_ITEMS:
        overflow = total_count - settings.MAX_HISTORY_ITEMS
        oldest_stmt = (
            select(DocumentRecord.id)
            .order_by(DocumentRecord.created_at.asc())
            .limit(overflow)
        )
        oldest_ids = (await session.execute(oldest_stmt)).scalars().all()
        for doc_id in oldest_ids:
            doc = await get_document(session, doc_id)
            if doc:
                await session.delete(doc)
        await session.commit()


async def create_document(
    session: AsyncSession,
    filename: str,
    mime: str,
    size_bytes: int,
    sha256: str,
    page_count: int,
    status: str,
    vendor_name: str,
    invoice_number: str,
    total_amount: float,
    currency: str,
    result_dict: dict[str, Any],
    grounding_dict: dict[str, Any] | None = None,
    processing_ms: int = 0,
    usage_dict: dict[str, Any] | None = None,
    page_images_bytes: list[bytes] | None = None,
) -> DocumentRecord:
    result_json_str = json.dumps(result_dict)
    grounding_json_str = json.dumps(grounding_dict) if grounding_dict else None
    usage_json_str = json.dumps(usage_dict) if usage_dict else None

    doc = DocumentRecord(
        filename=filename,
        mime=mime,
        size_bytes=size_bytes,
        sha256=sha256,
        page_count=page_count,
        status=status,
        vendor_name=vendor_name,
        invoice_number=invoice_number,
        total_amount=total_amount,
        currency=currency,
        result_json=result_json_str,
        original_result_json=result_json_str,
        grounding_json=grounding_json_str,
        processing_ms=processing_ms,
        usage_json=usage_json_str,
    )
    session.add(doc)
    await session.flush()

    if page_images_bytes:
        for idx, img_bytes in enumerate(page_images_bytes):
            p_rec = PageImageRecord(
                document_id=doc.id,
                page=idx + 1,
                jpeg_bytes=img_bytes,
            )
            session.add(p_rec)

    await session.commit()
    await session.refresh(doc)
    await enforce_history_cap(session)
    return doc


async def save_edits(
    session: AsyncSession,
    document_id: str,
    edits: list[dict[str, Any]],
    editor: str = "reviewer",
) -> DocumentRecord | None:
    doc = await get_document(session, document_id)
    if not doc:
        return None

    data = json.loads(doc.result_json)
    invoice = data.get("extracted_data", {})

    for edit in edits:
        field_path = edit.get("field_path", "")
        new_val = edit.get("value")
        old_val = ""

        if field_path.startswith("line_items."):
            parts = field_path.split(".")
            if len(parts) == 3:
                r_idx = int(parts[1])
                prop = parts[2]
                items = invoice.get("line_items", [])
                if 0 <= r_idx < len(items):
                    old_val = str(items[r_idx].get(prop, ""))
                    items[r_idx][prop] = new_val
        else:
            old_val = str(invoice.get(field_path, ""))
            invoice[field_path] = new_val

        e_rec = EditRecord(
            document_id=doc.id,
            field_path=field_path,
            old_value=old_val,
            new_value=str(new_val),
            editor=editor,
        )
        session.add(e_rec)

    doc.result_json = json.dumps(data)
    doc.vendor_name = invoice.get("vendor_name", doc.vendor_name)
    doc.invoice_number = invoice.get("invoice_number", doc.invoice_number)
    doc.total_amount = float(invoice.get("total_amount", doc.total_amount))
    doc.currency = invoice.get("currency", doc.currency)

    await session.commit()
    await session.refresh(doc)
    return doc


async def approve_document(
    session: AsyncSession,
    document_id: str,
    approved_by: str = "reviewer",
    note: str = "",
) -> DocumentRecord | None:
    doc = await get_document(session, document_id)
    if not doc:
        return None

    app_rec = ApprovalRecord(
        document_id=doc.id,
        approved_by=approved_by,
        note=note,
    )
    session.add(app_rec)

    doc.status = "APPROVED"
    data = json.loads(doc.result_json)
    data["overall_status"] = "APPROVED"
    doc.result_json = json.dumps(data)

    await session.commit()
    await session.refresh(doc)
    return doc


async def delete_document(session: AsyncSession, document_id: str) -> bool:
    doc = await get_document(session, document_id)
    if not doc:
        return False
    await session.delete(doc)
    await session.commit()
    return True


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_document(self, document_id: str) -> DocumentRecord | None:
        return await get_document(self.session, document_id)

    async def list_documents(self, limit: int = 50, offset: int = 0) -> list[DocumentRecord]:
        return await list_documents(self.session, limit=limit)

    async def delete_document(self, document_id: str) -> bool:
        return await delete_document(self.session, document_id)

    async def record_field_edits(
        self,
        document_id: str,
        user_id: str,
        field_updates: dict[str, Any],
        reason: str | None = None,
    ) -> DocumentRecord | None:
        edits = [{"field_path": k, "value": v} for k, v in field_updates.items()]
        return await save_edits(self.session, document_id, edits, editor=user_id)

    async def record_approval(
        self, document_id: str, user_id: str, notes: str | None = None
    ) -> DocumentRecord | None:
        return await approve_document(
            self.session, document_id, approved_by=user_id, note=notes or ""
        )

