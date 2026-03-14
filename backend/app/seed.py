"""Seed script: generates synthetic transactions and trains initial model."""
import asyncio
import hashlib
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from app.config import settings
from app.ml.preprocess import preprocess_dataframe
from app.ml.train import train_model
from app.ml.model_store import save_model


def generate_synthetic_data(n: int = 5000, fraud_rate: float = 0.05) -> pd.DataFrame:
    random.seed(42)
    np.random.seed(42)

    records = []
    for i in range(n):
        is_fraud = random.random() < fraud_rate
        amount = np.random.lognormal(4, 1.5) if not is_fraud else np.random.lognormal(5.5, 1.8)
        amount = round(max(1, amount), 2)

        pm = random.choice(["credit_card", "debit_card", "paypal", "crypto", "bank_transfer"])
        if is_fraud and random.random() < 0.4:
            pm = "crypto"

        device = random.choice(["desktop", "mobile", "tablet"])
        hour = random.randint(0, 23)
        if is_fraud and random.random() < 0.5:
            hour = random.choice([2, 3, 4, 22, 23])

        day = random.randint(0, 6)
        billing_match = random.random() > (0.6 if is_fraud else 0.05)
        is_new = random.random() < (0.7 if is_fraud else 0.15)

        records.append({
            "merchant_id": f"merchant_{random.randint(1, 20)}",
            "amount": amount,
            "payment_method": pm,
            "user_id_hash": hashlib.sha256(f"user_{i}".encode()).hexdigest()[:16],
            "ip_hash": hashlib.sha256(f"ip_{i}".encode()).hexdigest()[:16],
            "email_domain": random.choice(["gmail.com", "yahoo.com", "hotmail.com", "proton.me", "tempmail.org"]),
            "is_new_user": is_new,
            "device_type": device,
            "billing_shipping_match": billing_match,
            "hour_of_day": hour,
            "day_of_week": day,
            "items_count": random.randint(1, 10),
            "is_fraud": int(is_fraud),
        })

    return pd.DataFrame(records)


def run_seed():
    print("Generating synthetic data...")
    df = generate_synthetic_data()
    csv_path = "data/demo_transactions.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(df)} transactions to {csv_path}")

    print("Training initial model...")
    X, y = preprocess_dataframe(df)
    model, metrics = train_model(X, y)
    print(f"Metrics: {metrics}")

    file_path, sha256 = save_model(model, settings.model_dir, "1.0")
    print(f"Model saved to {file_path} (SHA-256: {sha256[:16]}...)")

    # Save to DB
    async def save_to_db():
        from app.dependencies import engine, async_session
        from app.models.db import Base, Model as ModelRecord, AuditEntry

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session() as session:
            async with session.begin():
                session.add(ModelRecord(
                    version="1.0",
                    file_path=file_path,
                    sha256_hash=sha256,
                    is_active=True,
                    **metrics,
                ))
                session.add(AuditEntry(
                    event_type="training",
                    event_data={**metrics, "version": "1.0", "promoted": True, "message": "Initial seed model"},
                    model_version="1.0",
                ))

        await engine.dispose()

    asyncio.run(save_to_db())
    print("Seed complete!")


if __name__ == "__main__":
    run_seed()
