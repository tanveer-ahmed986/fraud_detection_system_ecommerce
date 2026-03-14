from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, cast, Date
from typing import Optional

from app.dependencies import get_db
from app.models.db import Prediction, Transaction, Model as ModelRecord
from app.schemas.dashboard import (
    DashboardSummary, TimeseriesPoint, PredictionListItem, PredictionListResponse
)

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    total_q = await db.execute(select(func.count()).select_from(Prediction))
    total = total_q.scalar() or 0

    fraud_q = await db.execute(
        select(func.count()).select_from(Prediction).where(Prediction.label == "fraud")
    )
    fraud_count = fraud_q.scalar() or 0

    avg_q = await db.execute(select(func.avg(Prediction.confidence)))
    avg_conf = round(float(avg_q.scalar() or 0), 4)

    model_q = await db.execute(
        select(ModelRecord).where(ModelRecord.is_active == True)
    )
    active_model = model_q.scalar_one_or_none()

    return DashboardSummary(
        total_predictions=total,
        fraud_count=fraud_count,
        legitimate_count=total - fraud_count,
        fraud_rate=round(fraud_count / total, 4) if total > 0 else 0,
        avg_confidence=avg_conf,
        model_version=active_model.version if active_model else "none",
        model_recall=active_model.recall if active_model else None,
        model_precision=active_model.precision if active_model else None,
        model_fpr=active_model.fpr if active_model else None,
    )


@router.get("/timeseries", response_model=list[TimeseriesPoint])
async def dashboard_timeseries(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(
            cast(Prediction.created_at, Date).label("date"),
            func.count().label("total"),
            func.sum(case((Prediction.label == "fraud", 1), else_=0)).label("fraud"),
        )
        .group_by(cast(Prediction.created_at, Date))
        .order_by(cast(Prediction.created_at, Date).desc())
        .limit(days)
    )
    result = await db.execute(query)
    rows = result.all()

    return [
        TimeseriesPoint(
            date=str(r.date),
            total=r.total,
            fraud=r.fraud,
            fraud_rate=round(r.fraud / r.total, 4) if r.total > 0 else 0,
        )
        for r in rows
    ]


@router.get("/predictions", response_model=PredictionListResponse)
async def dashboard_predictions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    label: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Prediction, Transaction).join(
        Transaction, Prediction.transaction_id == Transaction.id
    )
    count_query = select(func.count()).select_from(Prediction)

    if label:
        query = query.where(Prediction.label == label)
        count_query = count_query.where(Prediction.label == label)

    total = (await db.execute(count_query)).scalar()

    query = query.order_by(Prediction.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    predictions = [
        PredictionListItem(
            transaction_id=str(p.transaction_id),
            amount=t.amount,
            label=p.label,
            confidence=p.confidence,
            merchant_id=t.merchant_id,
            created_at=p.created_at,
            top_features=p.feature_contributions or [],
        )
        for p, t in rows
    ]

    return PredictionListResponse(
        total=total, page=page, page_size=page_size, predictions=predictions
    )


@router.get("/transaction/{transaction_id}")
async def get_transaction_detail(transaction_id: str, db: AsyncSession = Depends(get_db)):
    """Get full details for a specific transaction including prediction and all features."""
    from uuid import UUID

    try:
        txn_uuid = UUID(transaction_id)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid transaction ID format")

    query = select(Prediction, Transaction).join(
        Transaction, Prediction.transaction_id == Transaction.id
    ).where(Transaction.id == txn_uuid)

    result = await db.execute(query)
    row = result.first()

    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Transaction not found")

    pred, txn = row

    return {
        "transaction_id": str(txn.id),
        "amount": txn.amount,
        "merchant_id": txn.merchant_id,
        "payment_method": txn.payment_method,
        "user_id_hash": txn.user_id_hash,
        "ip_hash": txn.ip_hash,
        "email_domain": txn.email_domain,
        "is_new_user": txn.is_new_user,
        "device_type": txn.device_type,
        "billing_shipping_match": txn.billing_shipping_match,
        "hour_of_day": txn.hour_of_day,
        "day_of_week": txn.day_of_week,
        "items_count": txn.items_count,
        "created_at": txn.created_at,
        "label": pred.label,
        "confidence": pred.confidence,
        "threshold_used": pred.threshold_used,
        "model_version": pred.model_version,
        "latency_ms": pred.latency_ms,
        "top_features": pred.feature_contributions or [],
        "prediction_created_at": pred.created_at,
    }
