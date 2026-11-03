import time
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from config import get_settings

settings = get_settings()


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.refill_rate = refill_rate
        self.last_refill = time.monotonic()

    def consume(self, amount: float = 1.0) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.last_refill = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object, requests_per_minute: int = 60, burst: int = 10):
        super().__init__(app)  # type: ignore[arg-type]
        self.buckets: dict[str, TokenBucket] = {}
        self.rate = requests_per_minute / 60.0
        self.capacity = burst


    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in ("/health", "/health/deep", "/metrics", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        api_key = request.headers.get("X-API-Key", "")
        bucket_key = f"{client_ip}:{api_key}"

        if bucket_key not in self.buckets:
            self.buckets[bucket_key] = TokenBucket(capacity=self.capacity, refill_rate=self.rate)

        bucket = self.buckets[bucket_key]
        if not bucket.consume():
            retry_after = int(1.0 / self.rate)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please slow down.",
                    "request_id": getattr(request.state, "request_id", ""),
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
