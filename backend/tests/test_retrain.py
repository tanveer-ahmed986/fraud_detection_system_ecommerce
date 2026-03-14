import pytest
import numpy as np
from app.ml.train import train_model, check_metric_gates


class TestTrainModel:
    def test_returns_model_and_metrics(self):
        np.random.seed(42)
        X = np.random.rand(500, 17)
        y = (np.random.rand(500) > 0.9).astype(float)
        model, metrics = train_model(X, y)
        assert model is not None
        assert "recall" in metrics
        assert "precision" in metrics
        assert "f1_score" in metrics
        assert "fpr" in metrics
        assert "dataset_rows" in metrics
        assert metrics["dataset_rows"] == 500

    def test_metric_gates_pass(self):
        metrics = {"recall": 0.95, "fpr": 0.03}
        passed, msg = check_metric_gates(metrics)
        assert passed is True

    def test_metric_gates_fail_recall(self):
        metrics = {"recall": 0.80, "fpr": 0.03}
        passed, msg = check_metric_gates(metrics)
        assert passed is False
        assert "recall" in msg

    def test_metric_gates_fail_fpr(self):
        metrics = {"recall": 0.95, "fpr": 0.10}
        passed, msg = check_metric_gates(metrics)
        assert passed is False
        assert "FPR" in msg
