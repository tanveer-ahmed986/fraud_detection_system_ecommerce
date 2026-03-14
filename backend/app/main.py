import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.dependencies import engine
from app.models.db import Base
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.routers import health, predict, retrain, audit, dashboard, models

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Try to load active model
    try:
        from sqlalchemy import select
        from app.dependencies import async_session
        from app.models.db import Model as ModelRecord
        from app.ml.model_store import load_model
        from app.ml.predict import FraudPredictor

        async with async_session() as session:
            result = await session.execute(
                select(ModelRecord).where(ModelRecord.is_active == True)
            )
            active = result.scalar_one_or_none()
            if active:
                model = load_model(active.file_path, active.sha256_hash)
                app_state["predictor"] = FraudPredictor(model)
                app_state["model_version"] = active.version
                app_state["threshold"] = settings.fraud_threshold
                logger.info(f"Loaded model v{active.version}")
            else:
                logger.warning("No active model found")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")

    yield

    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Fraud Detection API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimiterMiddleware, max_requests=settings.rate_limit_per_second)

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(retrain.router)
app.include_router(audit.router)
app.include_router(dashboard.router)
app.include_router(models.router)
