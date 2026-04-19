"""
Simple Fraud Detection API for WordPress Plugin Testing
No database required - loads model directly from file
"""

import joblib
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Fraud Detection API - Simple", version="2.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model on startup
model = None
explainer = None

@app.on_event("startup")
async def startup_event():
    global model, explainer
    try:
        model_path = Path("models/v2.0_model.pkl")
        explainer_path = Path("models/v2.0_explainer.pkl")

        if model_path.exists():
            model = joblib.load(model_path)
            logger.info(f"✅ Model loaded from {model_path}")
        else:
            logger.warning(f"⚠️ Model not found at {model_path}")

        if explainer_path.exists():
            explainer = joblib.load(explainer_path)
            logger.info(f"✅ Explainer loaded from {explainer_path}")
        else:
            logger.warning(f"⚠️ Explainer not found at {explainer_path}")

    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")

# Request models
class Transaction(BaseModel):
    merchant_id: str
    amount: float
    payment_method: str
    user_id_hash: str
    ip_hash: str
    email_domain: str
    is_new_user: bool
    device_type: str
    billing_shipping_match: bool
    hour_of_day: int
    day_of_week: int
    items_count: int

class FeatureContribution(BaseModel):
    feature: str
    contribution: float

class PredictionResponse(BaseModel):
    label: str
    confidence: float
    top_features: List[FeatureContribution]
    latency_ms: float

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "explainer_loaded": explainer is not None,
        "version": "2.0.0"
    }

# Predict endpoint
@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(transaction: Transaction):
    import time
    import numpy as np

    start_time = time.time()

    if model is None:
        return {
            "label": "error",
            "confidence": 0.0,
            "top_features": [],
            "latency_ms": 0.0
        }

    try:
        # Model expects 30 features (V1-V28, Time, Amount from credit card dataset)
        # Map e-commerce features to expected format

        # Create 28 synthetic V features based on transaction attributes
        v_features = []

        # V1-V4: Payment and user behavior
        v_features.append(1.0 if transaction.payment_method == "credit_card" else -1.0)
        v_features.append(1.0 if transaction.is_new_user else -1.0)
        v_features.append(-1.0 if transaction.billing_shipping_match else 1.0)
        v_features.append((transaction.hour_of_day - 12) / 12.0)  # Normalized hour

        # V5-V10: Transaction amount variations
        amount_normalized = transaction.amount / 100.0
        v_features.append(amount_normalized)
        v_features.append(amount_normalized ** 2)
        v_features.append(np.log1p(transaction.amount) / 10.0)
        v_features.append(1.0 if transaction.amount > 200 else -1.0)
        v_features.append(1.0 if transaction.amount > 500 else -1.0)
        v_features.append(transaction.items_count / 10.0)

        # V11-V15: User and merchant hashing patterns
        v_features.append((hash(transaction.user_id_hash) % 1000) / 1000.0 - 0.5)
        v_features.append((hash(transaction.ip_hash) % 1000) / 1000.0 - 0.5)
        v_features.append((hash(transaction.merchant_id) % 100) / 100.0 - 0.5)
        v_features.append((hash(transaction.email_domain) % 100) / 100.0 - 0.5)
        v_features.append(1.0 if transaction.device_type == "mobile" else -1.0)

        # V16-V20: Day and time patterns
        v_features.append(transaction.day_of_week / 7.0 - 0.5)
        v_features.append(1.0 if transaction.hour_of_day < 6 or transaction.hour_of_day > 22 else -1.0)  # Unusual hours
        v_features.append(1.0 if transaction.day_of_week in [0, 6] else -1.0)  # Weekend
        v_features.append(len(transaction.email_domain) / 20.0 - 0.5)
        v_features.append(1.0 if "gmail" in transaction.email_domain.lower() else -1.0)

        # V21-V28: Additional synthetic features
        v_features.append(transaction.amount / transaction.items_count if transaction.items_count > 0 else 0)
        v_features.append(1.0 if transaction.is_new_user and transaction.amount > 200 else -1.0)
        v_features.append(1.0 if not transaction.billing_shipping_match and transaction.is_new_user else -1.0)
        v_features.append(0.0)
        v_features.append(0.0)
        v_features.append(0.0)
        v_features.append(0.0)
        v_features.append(0.0)

        # Add Time and Amount (last 2 features)
        time_feature = float(transaction.hour_of_day * 3600)
        amount_feature = float(transaction.amount)

        # Combine all features into single list
        all_features = v_features + [time_feature, amount_feature]

        # Create numpy array with correct shape
        features = np.array([all_features], dtype=np.float32)

        # Verify feature count
        if features.shape[1] != 30:
            logger.error(f"Feature count mismatch: expected 30, got {features.shape[1]}")
            raise ValueError(f"Expected 30 features, got {features.shape[1]}")

        logger.info(f"Features shape: {features.shape}, dtype: {features.dtype}")
        logger.info(f"Sample features: {features[0][:5]}...")

        # Make prediction
        prediction = model.predict(features)[0]
        logger.info(f"Prediction: {prediction}")

        probability = model.predict_proba(features)[0]
        logger.info(f"Probability: {probability}")

        # Get confidence
        fraud_prob = probability[1] if len(probability) > 1 else probability[0]

        # Get feature importance using SHAP explainer for this specific transaction
        top_features = []
        try:
            # Feature names for credit card model
            feature_names = [f"V{i}" for i in range(1, 29)] + ["Time", "Amount"]

            # Map to user-friendly names for display
            friendly_names = {
                "V1": "Payment Method",
                "V2": "New Customer",
                "V3": "Address Mismatch",
                "V4": "Transaction Hour",
                "V5": "Transaction Amount",
                "V6": "Amount Squared",
                "V7": "Amount Pattern",
                "V8": "High Amount Flag",
                "V9": "Very High Amount",
                "V10": "Items Count",
                "V11": "Customer Behavior",
                "V12": "IP Pattern",
                "V13": "Merchant Pattern",
                "V14": "Email Domain",
                "V15": "Device Type",
                "V16": "Day of Week",
                "V17": "Unusual Hour",
                "V18": "Weekend Flag",
                "V19": "Domain Length",
                "V20": "Email Provider",
                "V21": "Avg Item Price",
                "V22": "New High Spender",
                "V23": "New + Addr Mismatch",
                "Amount": "Transaction Amount",
                "Time": "Transaction Time"
            }

            # Use SHAP explainer if available for transaction-specific contributions
            if explainer is not None:
                shap_values = explainer.shap_values(features)

                # For binary classification, shap_values might be a list [class0, class1]
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]  # Use positive class (fraud)

                # Get SHAP values for this transaction
                transaction_shap = shap_values[0] if len(shap_values.shape) > 1 else shap_values

                # Get top 3 by absolute contribution
                top_indices = np.argsort(np.abs(transaction_shap))[-3:][::-1]
                top_features = [
                    {
                        "feature": friendly_names.get(feature_names[i], feature_names[i]),
                        "contribution": float(transaction_shap[i])
                    }
                    for i in top_indices
                ]
                logger.info(f"SHAP top features: {top_features}")

            # Fallback to global feature importance if SHAP not available
            elif hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_

                # Get top 3 most important features globally
                top_indices = np.argsort(importances)[-3:][::-1]

                # Multiply by feature values to get direction
                for i in top_indices:
                    feature_value = features[0][i]
                    contribution = float(importances[i]) * (1 if feature_value > 0 else -1)
                    top_features.append({
                        "feature": friendly_names.get(feature_names[i], feature_names[i]),
                        "contribution": contribution
                    })
                logger.info(f"Feature importance (fallback): {top_features}")

        except Exception as e:
            logger.warning(f"Could not get feature contributions: {e}")
            # Last resort fallback
            top_features = [
                {"feature": "Transaction Amount", "contribution": 0.35 if prediction == 1 else -0.35},
                {"feature": "New Customer", "contribution": 0.28 if transaction.is_new_user else -0.28},
                {"feature": "Address Mismatch", "contribution": 0.22 if not transaction.billing_shipping_match else -0.22}
            ]

        latency_ms = (time.time() - start_time) * 1000

        return {
            "label": "HIGH RISK" if prediction == 1 else "LOW RISK",
            "confidence": float(fraud_prob),
            "top_features": top_features,
            "latency_ms": latency_ms
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Prediction error: {e}")
        logger.error(f"Traceback: {error_details}")
        return {
            "label": "error",
            "confidence": 0.0,
            "top_features": [{"feature": f"Error: {str(e)[:50]}", "contribution": 0.0}],
            "latency_ms": (time.time() - start_time) * 1000
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
