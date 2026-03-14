import uuid
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.transaction import TransactionRequest, PredictionResponse, FeatureContribution
from app.models.db import Transaction, Prediction, AuditEntry

router = APIRouter(prefix="/api/v1", tags=["predict"])


@router.post("/predict", response_model=PredictionResponse)
async def predict_transaction(
    req: TransactionRequest,
    db: AsyncSession = Depends(get_db),
):
    from app.main import app_state

    predictor = app_state.get("predictor")
    model_version = app_state.get("model_version", "unknown")
    threshold = app_state.get("threshold", 0.5)

    if predictor is None:
        raise RuntimeError("Model not loaded")

    result = predictor.predict(req.model_dump(), threshold=threshold)

    txn_id = uuid.uuid4()
    txn = Transaction(
        id=txn_id,
        merchant_id=req.merchant_id,
        amount=req.amount,
        payment_method=req.payment_method,
        user_id_hash=req.user_id_hash,
        ip_hash=req.ip_hash,
        email_domain=req.email_domain,
        is_new_user=req.is_new_user,
        device_type=req.device_type,
        billing_shipping_match=req.billing_shipping_match,
        hour_of_day=req.hour_of_day,
        day_of_week=req.day_of_week,
        items_count=req.items_count,
    )

    pred = Prediction(
        id=uuid.uuid4(),
        transaction_id=txn_id,
        model_version=model_version,
        label=result["label"],
        confidence=result["confidence"],
        threshold_used=result["threshold_used"],
        feature_contributions=result["top_features"],
        latency_ms=result["latency_ms"],
        fallback_applied=False,
    )

    audit = AuditEntry(
        event_type="prediction",
        event_data={
            "transaction_id": str(txn_id),
            "label": result["label"],
            "confidence": result["confidence"],
            "latency_ms": result["latency_ms"],
            "model_version": model_version,
        },
        model_version=model_version,
    )

    # Save to database synchronously to ensure session is still valid
    db.add(txn)
    db.add(pred)
    db.add(audit)
    await db.commit()

    return PredictionResponse(
        transaction_id=txn_id,
        label=result["label"],
        confidence=result["confidence"],
        threshold_used=result["threshold_used"],
        top_features=[FeatureContribution(**f) for f in result["top_features"]],
        latency_ms=result["latency_ms"],
        fallback_applied=False,
    )
