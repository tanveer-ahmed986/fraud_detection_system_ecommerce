import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class FallbackMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, amount_limit: float = 50.0):
        super().__init__(app)
        self.amount_limit = amount_limit

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/v1/predict"):
            return await call_next(request)

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Prediction failed, applying fallback: {e}")
            try:
                body = await request._receive()
                import json
                data = json.loads(body.get("body", b"{}"))
                amount = float(data.get("amount", 0))
            except Exception:
                amount = 0

            if amount < self.amount_limit:
                return JSONResponse(
                    status_code=200,
                    content={
                        "transaction_id": None,
                        "label": "legitimate",
                        "confidence": 0.0,
                        "threshold_used": 0.5,
                        "top_features": [],
                        "latency_ms": 0,
                        "fallback_applied": True,
                        "message": "Model unavailable; transaction allowed (below threshold)",
                    },
                )
            else:
                return JSONResponse(
                    status_code=200,
                    content={
                        "transaction_id": None,
                        "label": "manual_review",
                        "confidence": 0.0,
                        "threshold_used": 0.5,
                        "top_features": [],
                        "latency_ms": 0,
                        "fallback_applied": True,
                        "message": "Model unavailable; transaction queued for manual review",
                    },
                )
