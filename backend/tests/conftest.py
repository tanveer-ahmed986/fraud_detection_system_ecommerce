import pytest
import numpy as np
from unittest.mock import MagicMock


@pytest.fixture
def sample_transaction():
    return {
        "merchant_id": "merchant_1",
        "amount": 99.99,
        "payment_method": "credit_card",
        "user_id_hash": "abc123",
        "ip_hash": "def456",
        "email_domain": "gmail.com",
        "is_new_user": False,
        "device_type": "desktop",
        "billing_shipping_match": True,
        "hour_of_day": 14,
        "day_of_week": 2,
        "items_count": 3,
    }


@pytest.fixture
def sample_fraud_transaction():
    return {
        "merchant_id": "merchant_5",
        "amount": 2500.00,
        "payment_method": "crypto",
        "user_id_hash": "xyz789",
        "ip_hash": "uvw321",
        "email_domain": "tempmail.org",
        "is_new_user": True,
        "device_type": "mobile",
        "billing_shipping_match": False,
        "hour_of_day": 3,
        "day_of_week": 6,
        "items_count": 1,
    }


@pytest.fixture
def trained_model():
    """Create a small trained model for testing."""
    from sklearn.ensemble import RandomForestClassifier
    np.random.seed(42)
    X = np.random.rand(200, 17)
    y = (np.random.rand(200) > 0.9).astype(float)
    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X, y)
    return clf
