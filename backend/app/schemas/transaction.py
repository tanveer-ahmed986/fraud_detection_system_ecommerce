from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class TransactionRequest(BaseModel):
    merchant_id: str = Field(..., max_length=100)
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., max_length=50)
    user_id_hash: str = Field(..., max_length=64)
    ip_hash: str = Field(..., max_length=64)
    email_domain: str = Field(..., max_length=100)
    is_new_user: bool = False
    device_type: str = Field(..., max_length=30)
    billing_shipping_match: bool = True
    hour_of_day: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    items_count: int = Field(1, ge=1)


class FeatureContribution(BaseModel):
    feature: str
    contribution: float


class PredictionResponse(BaseModel):
    transaction_id: UUID
    label: str
    confidence: float
    threshold_used: float
    top_features: list[FeatureContribution]
    latency_ms: float
    fallback_applied: bool

    model_config = {"from_attributes": True}
