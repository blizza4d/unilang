import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import get_settings
from db.models import Base
from db.session import engine, get_db, init_db
from main import app


@pytest_asyncio.fixture(autouse=True)
async def initialize_test_database():
    await init_db()
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture(autouse=True)
def clean_test_settings(monkeypatch):
    get_settings.cache_clear()
    settings = get_settings()
    monkeypatch.setattr(settings, "FEATURE_DEMO_MODE", True)
    yield
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    sample_path = Path(__file__).parent.parent / "demo" / "samples" / "english_clean_sample1.pdf"
    if sample_path.exists():
        return sample_path.read_bytes()
    return b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"


@pytest.fixture
def sample_png_bytes() -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
        b"\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf"
        b"\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
    )
