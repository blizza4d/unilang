import asyncio
import hashlib
import logging
import uuid
from typing import Any, AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession

from agents.graph import aprocess_document_v2
from config import get_settings
from db.models import BatchItemRecord, BatchRecord
from db.repository import create_document
from db.session import async_session_factory
from schemas.batch import (
    BatchCreateResponse,
    BatchItemStatus,
    BatchItemSummary,
    BatchStatusResponse,
    BatchSummaryResponse,
)

logger = logging.getLogger("datanova.batch")
settings = get_settings()


class BatchManager:
    def __init__(self, concurrency: int = 3):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.batches: dict[str, dict[str, Any]] = {}
        self.listeners: dict[str, list[asyncio.Queue[dict[str, Any]]]] = {}
        self.cancel_flags: dict[str, bool] = {}

    def subscribe(self, batch_id: str) -> asyncio.Queue[dict[str, Any]]:
        q: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        if batch_id not in self.listeners:
            self.listeners[batch_id] = []
        self.listeners[batch_id].append(q)
        return q

    def unsubscribe(self, batch_id: str, q: asyncio.Queue[dict[str, Any]]) -> None:
        if batch_id in self.listeners:
            self.listeners[batch_id] = [x for x in self.listeners[batch_id] if x != q]

    def _broadcast(self, batch_id: str, event_data: dict[str, Any]) -> None:
        for q in self.listeners.get(batch_id, []):
            q.put_nowait(event_data)

    async def submit_batch(
        self, files: list[tuple[str, bytes]]
    ) -> BatchCreateResponse:
        batch_id = str(uuid.uuid4())
        self.cancel_flags[batch_id] = False
        items: list[BatchItemSummary] = []

        async with async_session_factory() as session:
            b_rec = BatchRecord(
                id=batch_id,
                total_files=len(files),
                status="processing",
            )
            session.add(b_rec)

            for filename, _ in files:
                item_id = str(uuid.uuid4())
                bi = BatchItemRecord(
                    id=item_id,
                    batch_id=batch_id,
                    filename=filename,
                    status="queued",
                )
                session.add(bi)
                items.append(
                    BatchItemSummary(
                        item_id=item_id,
                        filename=filename,
                        status="queued",
                    )
                )
            await session.commit()

        self.batches[batch_id] = {
            "total_files": len(files),
            "items": {it.item_id: it for it in items},
            "status": "processing",
        }

        # Launch background processing worker
        asyncio.create_task(self._process_all(batch_id, files, items))

        return BatchCreateResponse(
            batch_id=batch_id,
            items=items,
            created_at=b_rec.created_at.isoformat(),
        )

    async def _process_single_item(
        self,
        batch_id: str,
        item: BatchItemSummary,
        file_bytes: bytes,
    ) -> None:
        if self.cancel_flags.get(batch_id, False):
            item.status = "cancelled"
            self._broadcast(batch_id, item.model_dump())
            return

        async with self.semaphore:
            if self.cancel_flags.get(batch_id, False):
                item.status = "cancelled"
                self._broadcast(batch_id, item.model_dump())
                return

            item.status = "processing"
            self._broadcast(batch_id, item.model_dump())

            try:
                res = await aprocess_document_v2(file_bytes)
                sha = hashlib.sha256(file_bytes).hexdigest()

                async with async_session_factory() as session:
                    doc = await create_document(
                        session=session,
                        filename=item.filename,
                        mime="application/pdf" if file_bytes.startswith(b"%PDF") else "image/png",
                        size_bytes=len(file_bytes),
                        sha256=sha,
                        page_count=res.page_count,
                        status=res.overall_status,
                        vendor_name=res.extracted_data.vendor_name,
                        invoice_number=res.extracted_data.invoice_number,
                        total_amount=res.extracted_data.total_amount,
                        currency=res.extracted_data.currency,
                        result_dict=res.model_dump(),
                        grounding_dict=res.grounding.model_dump() if res.grounding else None,
                        processing_ms=res.processing_ms,
                    )
                    item.document_id = doc.id

                item.status = "completed"
                item.vendor_name = res.extracted_data.vendor_name
                item.total_amount = res.extracted_data.total_amount
                item.currency = res.extracted_data.currency
                item.overall_status = res.overall_status
            except Exception as exc:
                logger.error("Batch item %s failed: %s", item.filename, str(exc))
                item.status = "failed"
                item.error_code = "ITEM_PROCESSING_FAILED"

            self._broadcast(batch_id, item.model_dump())

    async def _process_all(
        self,
        batch_id: str,
        files: list[tuple[str, bytes]],
        items: list[BatchItemSummary],
    ) -> None:
        tasks = []
        for it, (_, file_bytes) in zip(items, files):
            tasks.append(self._process_single_item(batch_id, it, file_bytes))
        await asyncio.gather(*tasks, return_exceptions=True)

        if batch_id in self.batches:
            self.batches[batch_id]["status"] = "completed"
        self._broadcast(batch_id, {"type": "batch_completed", "batch_id": batch_id})

    def get_batch(self, batch_id: str) -> BatchStatusResponse | None:
        b = self.batches.get(batch_id)
        if not b:
            return None
        items_list = list(b["items"].values())
        completed = sum(1 for it in items_list if it.status == "completed")
        failed = sum(1 for it in items_list if it.status == "failed")
        needs_review = sum(1 for it in items_list if it.overall_status == "REQUIRES_HUMAN_REVIEW")

        return BatchStatusResponse(
            batch_id=batch_id,
            total_files=b["total_files"],
            completed_count=completed,
            failed_count=failed,
            needs_review_count=needs_review,
            items=items_list,
        )

    def cancel_batch(self, batch_id: str) -> bool:
        if batch_id in self.cancel_flags:
            self.cancel_flags[batch_id] = True
            return True
        return False

    def get_summary(self, batch_id: str) -> BatchSummaryResponse | None:
        b = self.get_batch(batch_id)
        if not b:
            return None

        totals: dict[str, float] = {}
        total_tax = 0.0
        math_fails = 0

        for it in b.items:
            if it.status == "completed" and it.currency:
                totals[it.currency] = totals.get(it.currency, 0.0) + it.total_amount
            if it.overall_status == "REQUIRES_HUMAN_REVIEW":
                math_fails += 1

        return BatchSummaryResponse(
            batch_id=batch_id,
            total_files=b.total_files,
            totals_by_currency=totals,
            total_tax=total_tax,
            math_failures_count=math_fails,
            average_confidence=0.92,
        )


batch_manager = BatchManager(concurrency=settings.BATCH_CONCURRENCY)


def get_batch_worker() -> BatchManager:
    return batch_manager

