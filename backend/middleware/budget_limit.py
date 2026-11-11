import time
from datetime import datetime, timezone
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from config import get_settings


class BudgetLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object):
        super().__init__(app)  # type: ignore[arg-type]
        self.daily_spend: float = 0.0
        self.hourly_spend: float = 0.0
        now = datetime.now(timezone.utc)
        self.last_day: int = now.day
        self.last_hour: int = now.hour

    def _refresh_windows(self) -> None:
        now = datetime.now(timezone.utc)
        if now.day != self.last_day:
            self.daily_spend = 0.0
            self.last_day = now.day
        if now.hour != self.last_hour:
            self.hourly_spend = 0.0
            self.last_hour = now.hour

    def record_cost(self, cost: float) -> None:
        self._refresh_windows()
        self.daily_spend += cost
        self.hourly_spend += cost

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        self._refresh_windows()
        settings = get_settings()

        # Chaos Simulation Hook (active only if CHAOS_MODE is explicitly enabled)
        if settings.CHAOS_MODE and request.headers.get("X-Chaos-Simulate"):
            chaos_type = request.headers.get("X-Chaos-Simulate")
            if chaos_type == "500":
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=500,
                    content={
                        "error_code": "INTERNAL_ERROR",
                        "message": "Chaos simulated 500 internal server error.",
                        "request_id": getattr(request.state, "request_id", "chaos-500"),
                    },
                )
            elif chaos_type == "corrupt_json":
                from fastapi.responses import Response as RawResponse
                return RawResponse(
                    content=b"{invalid_json_payload:true,",
                    status_code=200,
                    media_type="application/json",
                )
            elif chaos_type == "timeout":
                import asyncio
                await asyncio.sleep(5)

        # Check spend limits
        is_exceeded = (
            self.daily_spend >= settings.DAILY_BUDGET_USD
            or self.hourly_spend >= settings.HOURLY_BUDGET_USD
        )
        request.state.budget_exceeded = is_exceeded
        request.state.current_daily_spend = self.daily_spend
        request.state.current_hourly_spend = self.hourly_spend

        response = await call_next(request)

        if is_exceeded:
            response.headers["X-Budget-Fallback"] = (
                "Live AI paused to control cost; running in demo mode."
            )

        return response
