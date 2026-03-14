from pydantic import BaseModel
from datetime import datetime


class DashboardSummary(BaseModel):
    total_predictions: int
    fraud_count: int
    legitimate_count: int
    fraud_rate: float
    avg_confidence: float
    model_version: str
    model_recall: float | None
    model_precision: float | None
    model_fpr: float | None


class TimeseriesPoint(BaseModel):
    date: str
    total: int
    fraud: int
    fraud_rate: float


class PredictionListItem(BaseModel):
    transaction_id: str
    amount: float
    label: str
    confidence: float
    merchant_id: str
    created_at: datetime
    top_features: list[dict]

    model_config = {"from_attributes": True}


class PredictionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    predictions: list[PredictionListItem]
