import numpy as np
from typing import Any


PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "crypto", "bank_transfer"]
DEVICE_TYPES = ["desktop", "mobile", "tablet"]

FEATURE_NAMES: list[str] = []


def _build_feature_names() -> list[str]:
    names = [
        "amount", "log_amount", "is_new_user", "billing_shipping_match",
        "items_count", "hour_sin", "hour_cos", "day_sin", "day_cos",
    ]
    for pm in PAYMENT_METHODS:
        names.append(f"pm_{pm}")
    for dt in DEVICE_TYPES:
        names.append(f"dev_{dt}")
    return names


FEATURE_NAMES = _build_feature_names()


def preprocess_transaction(data: dict[str, Any]) -> np.ndarray:
    amount = float(data["amount"])
    log_amount = np.log1p(amount)
    is_new_user = float(data.get("is_new_user", False))
    billing_match = float(data.get("billing_shipping_match", True))
    items_count = float(data.get("items_count", 1))

    hour = int(data["hour_of_day"])
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)

    day = int(data["day_of_week"])
    day_sin = np.sin(2 * np.pi * day / 7)
    day_cos = np.cos(2 * np.pi * day / 7)

    features = [amount, log_amount, is_new_user, billing_match, items_count,
                hour_sin, hour_cos, day_sin, day_cos]

    pm = data.get("payment_method", "").lower()
    for method in PAYMENT_METHODS:
        features.append(1.0 if pm == method else 0.0)

    dev = data.get("device_type", "").lower()
    for dtype in DEVICE_TYPES:
        features.append(1.0 if dev == dtype else 0.0)

    return np.array(features, dtype=np.float64).reshape(1, -1)


def preprocess_dataframe(df) -> tuple[np.ndarray, np.ndarray]:
    """Preprocess a pandas DataFrame for training. Expects 'is_fraud' column as label."""
    import pandas as pd

    rows = []
    for _, row in df.iterrows():
        data = row.to_dict()
        feat = preprocess_transaction(data).flatten()
        rows.append(feat)

    X = np.array(rows)
    y = df["is_fraud"].values.astype(np.float64)
    return X, y
