import time
import asyncio
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: float = 1.0):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/v1/predict"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        async with self._lock:
            self.requests[client_ip] = [
                t for t in self.requests[client_ip] if now - t < self.window
            ]
            if len(self.requests[client_ip]) >= self.max_requests:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            self.requests[client_ip].append(now)

        return await call_next(request)
