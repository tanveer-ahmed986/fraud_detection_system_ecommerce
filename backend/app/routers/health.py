from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
async def health_check():
    from app.main import app_state
    model_loaded = app_state.get("predictor") is not None
    model_version = app_state.get("model_version", "none")
    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "model_version": model_version,
    }
