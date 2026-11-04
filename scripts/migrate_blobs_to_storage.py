"""One-off migration script: extracts page image BLOBs to ObjectStore."""

import asyncio
import logging
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, update
from db.models import DocumentRecord, PageImageRecord
from db.session import async_session_factory
from storage.factory import get_storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate_blobs")


async def migrate_blobs() -> None:
    storage = get_storage()
    logger.info("Starting BLOB to ObjectStore migration using backend: %s", type(storage).__name__)

    migrated_count = 0
    total_bytes = 0

    async with async_session_factory() as session:
        result = await session.execute(
            select(PageImageRecord).where(PageImageRecord.jpeg_bytes.isnot(None))
        )
        page_records = result.scalars().all()

        logger.info("Found %d page image records with inline BLOBs to migrate.", len(page_records))

        for page in page_records:
            doc_result = await session.execute(
                select(DocumentRecord).where(DocumentRecord.id == page.document_id)
            )
            doc = doc_result.scalar_one_or_none()
            tenant_id = getattr(doc, "tenant_id", "default") if doc else "default"

            key = f"{tenant_id}/{page.document_id}/pages/{page.page}.jpg"

            if page.jpeg_bytes:
                await storage.put(key, page.jpeg_bytes, content_type="image/jpeg")
                total_bytes += len(page.jpeg_bytes)

                await session.execute(
                    update(PageImageRecord)
                    .where(PageImageRecord.id == page.id)
                    .values(storage_key=key, jpeg_bytes=None)
                )
                migrated_count += 1

        await session.commit()

    logger.info(
        "Successfully migrated %d page image records (%0.2f MB) to object storage.",
        migrated_count,
        total_bytes / (1024 * 1024),
    )


if __name__ == "__main__":
    asyncio.run(migrate_blobs())
