import time
import numpy as np
import shap
from typing import Any

from app.ml.preprocess import preprocess_transaction, FEATURE_NAMES


class FraudPredictor:
    """Holds a loaded model + cached SHAP explainer for fast inference."""

    def __init__(self, model: Any):
        self.model = model
        self.explainer = shap.TreeExplainer(model)

    def predict(self, transaction_data: dict, threshold: float = 0.5) -> dict:
        start = time.time()

        features = preprocess_transaction(transaction_data)
        proba = self.model.predict_proba(features)[0]
        fraud_prob = float(proba[1])
        label = "fraud" if fraud_prob >= threshold else "legitimate"

        shap_values = self.explainer.shap_values(features)
        # For binary classification, shap_values may be a list [class0, class1]
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        else:
            sv = shap_values[0]

        # Ensure sv is a 1D array to avoid sorting errors
        sv = np.asarray(sv).flatten()

        contributions = sorted(
            zip(FEATURE_NAMES, sv),
            key=lambda x: abs(x[1]),
            reverse=True,
        )[:3]

        top_features = [
            {"feature": name, "contribution": round(float(val), 4)}
            for name, val in contributions
        ]

        latency_ms = round((time.time() - start) * 1000, 2)

        return {
            "label": label,
            "confidence": round(fraud_prob, 4),
            "threshold_used": threshold,
            "top_features": top_features,
            "latency_ms": latency_ms,
        }
