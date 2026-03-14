from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditEntryResponse(BaseModel):
    id: int
    event_type: str
    event_data: dict
    model_version: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    entries: list[AuditEntryResponse]
