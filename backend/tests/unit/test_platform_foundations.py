import os
import shutil
import pytest
from pathlib import Path
from storage.local import LocalObjectStore
from cache.redis_cache import AsyncCache
from db.health import check_database_health


@pytest.fixture
def temp_storage_dir(tmp_path: Path):
    store_dir = tmp_path / "test_store"
    store_dir.mkdir()
    yield store_dir
    if store_dir.exists():
        shutil.rmtree(store_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_local_storage_put_get_delete(temp_storage_dir: Path):
    store = LocalObjectStore(base_dir=str(temp_storage_dir))
    key = "tenant_123/doc_abc/pages/1.jpg"
    data = b"\xff\xd8\xff\xe0\x00\x10JFIF"

    # Put
    res_key = await store.put(key, data, content_type="image/jpeg")
    assert res_key == key

    # Exists
    assert await store.exists(key) is True

    # Get
    retrieved = await store.get(key)
    assert retrieved == data

    # List prefix
    listed = await store.list_prefix("tenant_123")
    assert any("1.jpg" in k for k in listed)

    # Delete
    deleted = await store.delete(key)
    assert deleted is True
    assert await store.exists(key) is False


@pytest.mark.asyncio
async def test_local_storage_path_traversal_protection(temp_storage_dir: Path):
    store = LocalObjectStore(base_dir=str(temp_storage_dir))
    malicious_key = "../../etc/passwd"

    with pytest.raises(ValueError, match="Path traversal"):
        await store.put(malicious_key, b"evil")

    with pytest.raises(ValueError, match="Path traversal"):
        await store.get(malicious_key)


@pytest.mark.asyncio
async def test_cache_memory_fallback():
    cache = AsyncCache()
    key = "test_capability_key"
    val = {"streaming": True, "ocr": False}

    await cache.set(key, val, ttl_seconds=60, namespace="test")
    cached = await cache.get(key, namespace="test")
    assert cached == val

    # Non-existent key
    assert await cache.get("nonexistent", namespace="test") is None

    # Delete
    deleted = await cache.delete(key, namespace="test")
    assert deleted is True
    assert await cache.get(key, namespace="test") is None


@pytest.mark.asyncio
async def test_db_health_check():
    health = await check_database_health()
    assert health["status"] in ("healthy", "unhealthy")
    assert "latency_ms" in health
    assert "current_revision" in health
