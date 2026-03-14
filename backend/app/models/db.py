import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Boolean, Integer, BigInteger, DateTime,
    ForeignKey, Text, Index, CheckConstraint, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    user_id_hash = Column(String(64), nullable=False)
    ip_hash = Column(String(64), nullable=False)
    email_domain = Column(String(100), nullable=False)
    is_new_user = Column(Boolean, nullable=False, default=False)
    device_type = Column(String(30), nullable=False)
    billing_shipping_match = Column(Boolean, nullable=False, default=True)
    hour_of_day = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    items_count = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    prediction = relationship("Prediction", back_populates="transaction", uselist=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_amount_positive"),
        CheckConstraint("hour_of_day >= 0 AND hour_of_day <= 23", name="ck_hour_valid"),
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="ck_day_valid"),
        CheckConstraint("items_count >= 1", name="ck_items_positive"),
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False, unique=True)
    model_version = Column(String(20), nullable=False)
    label = Column(String(15), nullable=False)  # fraud / legitimate
    confidence = Column(Float, nullable=False)
    threshold_used = Column(Float, nullable=False)
    feature_contributions = Column(JSONB, nullable=False)  # top-3
    latency_ms = Column(Float, nullable=False)
    fallback_applied = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="prediction")

    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_confidence_range"),
    )


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(20), nullable=False, unique=True)
    file_path = Column(String(255), nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    recall = Column(Float)
    precision = Column(Float)
    f1_score = Column(Float)
    fpr = Column(Float)
    dataset_rows = Column(Integer)
    dataset_fraud_pct = Column(Float)
    training_duration_s = Column(Float)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AuditEntry(Base):
    __tablename__ = "audit_entries"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_type = Column(String(30), nullable=False, index=True)
    event_data = Column(JSONB, nullable=False)
    model_version = Column(String(20))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class MerchantConfig(Base):
    __tablename__ = "merchant_configs"

    merchant_id = Column(String(100), primary_key=True)
    api_endpoint = Column(String(500))
    fraud_threshold = Column(Float, nullable=False, default=0.50)
    fallback_amount_limit = Column(Float, nullable=False, default=50.0)
    notifications_enabled = Column(Boolean, nullable=False, default=True)
    api_key_hash = Column(String(64))
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
