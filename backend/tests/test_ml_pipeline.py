import pytest
import os
import tempfile
import numpy as np
from app.ml.model_store import save_model, load_model, compute_sha256
from app.ml.preprocess import preprocess_dataframe


class TestModelStore:
    def test_save_and_load(self, trained_model):
        with tempfile.TemporaryDirectory() as tmpdir:
            path, sha = save_model(trained_model, tmpdir, "1.0")
            assert os.path.exists(path)
            assert len(sha) == 64

            loaded = load_model(path, sha)
            assert loaded is not None

    def test_integrity_check_fails(self, trained_model):
        with tempfile.TemporaryDirectory() as tmpdir:
            path, sha = save_model(trained_model, tmpdir, "1.0")
            with pytest.raises(ValueError, match="integrity"):
                load_model(path, "wrong_hash")

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_model("/nonexistent/model.joblib")


class TestPreprocessDataframe:
    def test_preprocess_dataframe(self):
        import pandas as pd
        df = pd.DataFrame([{
            "merchant_id": "m1", "amount": 100, "payment_method": "credit_card",
            "user_id_hash": "abc", "ip_hash": "def", "email_domain": "test.com",
            "is_new_user": False, "device_type": "desktop",
            "billing_shipping_match": True, "hour_of_day": 12,
            "day_of_week": 3, "items_count": 2, "is_fraud": 0,
        }])
        X, y = preprocess_dataframe(df)
        assert X.shape[0] == 1
        assert y.shape[0] == 1
        assert y[0] == 0.0
