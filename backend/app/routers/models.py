from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.config import settings
from app.dependencies import get_db
from app.models.db import Model as ModelRecord, AuditEntry
from app.ml.model_store import load_model
from app.ml.predict import FraudPredictor

router = APIRouter(prefix="/api/v1", tags=["models"])


@router.get("/models")
async def list_models(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ModelRecord).order_by(ModelRecord.created_at.desc()))
    models = result.scalars().all()
    return [
        {
            "version": m.version,
            "is_active": m.is_active,
            "recall": m.recall,
            "precision": m.precision,
            "f1_score": m.f1_score,
            "fpr": m.fpr,
            "dataset_rows": m.dataset_rows,
            "created_at": m.created_at.isoformat(),
        }
        for m in models
    ]


@router.post("/models/{version}/activate")
async def activate_model(
    version: str,
    db: AsyncSession = Depends(get_db),
    x_api_key: str = Header(...),
):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")

    result = await db.execute(select(ModelRecord).where(ModelRecord.version == version))
    model_record = result.scalar_one_or_none()
    if not model_record:
        raise HTTPException(status_code=404, detail=f"Model version {version} not found")

    model = load_model(model_record.file_path, model_record.sha256_hash)

    await db.execute(update(ModelRecord).values(is_active=False))
    model_record.is_active = True
    db.add(AuditEntry(
        event_type="rollback",
        event_data={"activated_version": version},
        model_version=version,
    ))
    await db.commit()

    from app.main import app_state
    app_state["predictor"] = FraudPredictor(model)
    app_state["model_version"] = version

    return {"message": f"Model {version} activated", "version": version}
