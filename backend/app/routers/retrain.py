import pandas as pd
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.config import settings
from app.dependencies import get_db
from app.schemas.training import RetrainRequest, RetrainResponse
from app.models.db import Model as ModelRecord, AuditEntry
from app.ml.preprocess import preprocess_dataframe
from app.ml.train import train_model, check_metric_gates
from app.ml.model_store import save_model
from app.ml.predict import FraudPredictor

router = APIRouter(prefix="/api/v1", tags=["retrain"])


@router.post("/retrain", response_model=RetrainResponse)
async def retrain(
    req: RetrainRequest,
    db: AsyncSession = Depends(get_db),
    x_api_key: str = Header(...),
):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")

    dataset_path = req.dataset_path or "data/demo_transactions.csv"
    df = pd.read_csv(dataset_path)
    X, y = preprocess_dataframe(df)

    model, metrics = train_model(X, y)
    passed, message = check_metric_gates(metrics, req.min_recall, req.max_fpr)

    # Determine next version
    from sqlalchemy import func, select
    result = await db.execute(select(func.count()).select_from(ModelRecord))
    count = result.scalar()
    version = f"{count + 1}.0"

    file_path, sha256 = save_model(model, settings.model_dir, version)

    model_record = ModelRecord(
        version=version,
        file_path=file_path,
        sha256_hash=sha256,
        is_active=passed,
        recall=metrics["recall"],
        precision=metrics["precision"],
        f1_score=metrics["f1_score"],
        fpr=metrics["fpr"],
        dataset_rows=metrics["dataset_rows"],
        dataset_fraud_pct=metrics["dataset_fraud_pct"],
        training_duration_s=metrics["training_duration_s"],
    )

    if passed:
        await db.execute(update(ModelRecord).values(is_active=False))

    db.add(model_record)
    db.add(AuditEntry(
        event_type="training",
        event_data={**metrics, "version": version, "promoted": passed, "message": message},
        model_version=version,
    ))
    await db.commit()

    if passed:
        from app.main import app_state
        app_state["predictor"] = FraudPredictor(model)
        app_state["model_version"] = version

    return RetrainResponse(
        version=version,
        promoted=passed,
        message=message,
        **metrics,
    )
