import pytest
from app.ml.preprocess import preprocess_transaction, FEATURE_NAMES


class TestPreprocess:
    def test_output_shape(self, sample_transaction):
        result = preprocess_transaction(sample_transaction)
        assert result.shape == (1, len(FEATURE_NAMES))

    def test_log_amount(self, sample_transaction):
        import numpy as np
        result = preprocess_transaction(sample_transaction)
        assert result[0][1] == pytest.approx(np.log1p(99.99), rel=1e-4)

    def test_one_hot_payment(self, sample_transaction):
        result = preprocess_transaction(sample_transaction)
        # credit_card is index 0 in PAYMENT_METHODS, feature starts at index 9
        assert result[0][9] == 1.0  # credit_card
        assert result[0][10] == 0.0  # debit_card

    def test_hour_encoding(self, sample_transaction):
        import numpy as np
        result = preprocess_transaction(sample_transaction)
        hour = 14
        expected_sin = np.sin(2 * np.pi * hour / 24)
        assert result[0][5] == pytest.approx(expected_sin, rel=1e-4)


class TestPrediction:
    def test_predict_returns_required_fields(self, trained_model, sample_transaction):
        from app.ml.predict import FraudPredictor
        predictor = FraudPredictor(trained_model)
        result = predictor.predict(sample_transaction)
        assert "label" in result
        assert "confidence" in result
        assert "top_features" in result
        assert "latency_ms" in result
        assert result["label"] in ("fraud", "legitimate")
        assert 0 <= result["confidence"] <= 1
        assert len(result["top_features"]) == 3

    def test_predict_top_features_have_names(self, trained_model, sample_transaction):
        from app.ml.predict import FraudPredictor
        predictor = FraudPredictor(trained_model)
        result = predictor.predict(sample_transaction)
        for feat in result["top_features"]:
            assert "feature" in feat
            assert "contribution" in feat
