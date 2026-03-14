from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import Optional

from app.dependencies import get_db
from app.models.db import AuditEntry
from app.schemas.audit import AuditListResponse, AuditEntryResponse

router = APIRouter(prefix="/api/v1", tags=["audit"])


@router.get("/audit", response_model=AuditListResponse)
async def list_audit(
    event_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditEntry)
    count_query = select(func.count()).select_from(AuditEntry)

    if event_type:
        query = query.where(AuditEntry.event_type == event_type)
        count_query = count_query.where(AuditEntry.event_type == event_type)
    if start_date:
        query = query.where(AuditEntry.created_at >= start_date)
        count_query = count_query.where(AuditEntry.created_at >= start_date)
    if end_date:
        query = query.where(AuditEntry.created_at <= end_date)
        count_query = count_query.where(AuditEntry.created_at <= end_date)

    total = (await db.execute(count_query)).scalar()

    query = query.order_by(AuditEntry.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    entries = result.scalars().all()

    return AuditListResponse(
        total=total,
        page=page,
        page_size=page_size,
        entries=[AuditEntryResponse.model_validate(e) for e in entries],
    )
