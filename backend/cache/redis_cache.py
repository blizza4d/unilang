import asyncio
import json
import logging
import time
from typing import Any, Dict, Optional
from config import get_settings

logger = logging.getLogger("datanova.cache")


class AsyncCache:
    """Typed async cache with Redis backend and automatic memory fallback."""

    def __init__(self) -> None:
        self._memory_store: Dict[str, tuple[float, Any]] = {}
        self._redis_client: Optional[Any] = None
        self._initialized = False

    async def _get_redis(self) -> Optional[Any]:
        if not self._initialized:
            settings = get_settings()
            redis_url = getattr(settings, "REDIS_URL", None)
            if redis_url and getattr(settings, "QUEUE_BACKEND", "inline") == "redis":
                try:
                    import redis.asyncio as aioredis
                    self._redis_client = aioredis.from_url(redis_url, decode_responses=True)
                    await self._redis_client.ping()
                except Exception as exc:
                    logger.info("Redis not reachable (%s); falling back to in-memory cache", exc)
                    self._redis_client = None
            self._initialized = True
        return self._redis_client

    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        full_key = f"{namespace}:{key}"
        r = await self._get_redis()
        if r is not None:
            try:
                raw = await r.get(full_key)
                if raw is not None:
                    return json.loads(raw)
                return None
            except Exception as exc:
                logger.debug("Redis cache get error: %s", exc)

        # In-memory fallback
        item = self._memory_store.get(full_key)
        if item:
            expires_at, val = item
            if time.time() < expires_at:
                return val
            del self._memory_store[full_key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300, namespace: str = "default") -> bool:
        full_key = f"{namespace}:{key}"
        r = await self._get_redis()
        if r is not None:
            try:
                await r.setex(full_key, ttl_seconds, json.dumps(value))
                return True
            except Exception as exc:
                logger.debug("Redis cache set error: %s", exc)

        # In-memory fallback
        self._memory_store[full_key] = (time.time() + ttl_seconds, value)
        return True

    async def delete(self, key: str, namespace: str = "default") -> bool:
        full_key = f"{namespace}:{key}"
        r = await self._get_redis()
        if r is not None:
            try:
                await r.delete(full_key)
                return True
            except Exception:
                pass
        if full_key in self._memory_store:
            del self._memory_store[full_key]
            return True
        return False

    async def clear_namespace(self, namespace: str) -> int:
        count = 0
        r = await self._get_redis()
        if r is not None:
            try:
                async for key in r.scan_iter(f"{namespace}:*"):
                    await r.delete(key)
                    count += 1
                return count
            except Exception:
                pass

        keys_to_del = [k for k in self._memory_store if k.startswith(f"{namespace}:")]
        for k in keys_to_del:
            del self._memory_store[k]
            count += 1
        return count


# Global cache instance
cache = AsyncCache()
