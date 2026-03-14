from pydantic import BaseModel, Field
from typing import Optional


class RetrainRequest(BaseModel):
    dataset_path: Optional[str] = None
    min_recall: float = Field(0.90, ge=0, le=1)
    max_fpr: float = Field(0.05, ge=0, le=1)


class RetrainResponse(BaseModel):
    version: str
    recall: float
    precision: float
    f1_score: float
    fpr: float
    dataset_rows: int
    dataset_fraud_pct: float
    training_duration_s: float
    promoted: bool
    message: str
