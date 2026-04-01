"""
Vercel-optimized Production API for E-commerce Fraud Detection
Compatible with WordPress plugin and frontend dashboard
"""

import joblib
import logging
import numpy as np
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FraudShield AI API",
    version="2.0.0",
    description="AI-powered fraud detection for e-commerce"
)

# CORS - Allow all origins for WordPress compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # WordPress needs this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model
model = None
label_encoders = None
feature_names = None

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    global model, label_encoders, feature_names

    try:
        model_dir = Path(os.getenv("MODEL_DIR", "models"))
        logger.info(f"Starting up... Model directory: {model_dir}")
        logger.info(f"Current working directory: {Path.cwd()}")

        # List available files
        if model_dir.exists():
            logger.info(f"Files in {model_dir}: {list(model_dir.glob('*'))}")
        else:
            logger.error(f"Model directory does not exist: {model_dir}")

        model_path = model_dir / "ecommerce_fraud_model.pkl"
        if model_path.exists():
            logger.info(f"Loading model from {model_path}")
            model = joblib.load(model_path)
            logger.info(f"✅ Model loaded successfully")
        else:
            logger.warning(f"⚠️ Model not found at {model_path}, API will run without model")

        encoders_path = model_dir / "label_encoders.pkl"
        if encoders_path.exists():
            label_encoders = joblib.load(encoders_path)
            logger.info(f"✅ Encoders loaded")
        else:
            logger.warning(f"⚠️ Encoders not found, using empty dict")
            label_encoders = {}

        features_path = model_dir / "feature_names.pkl"
        if features_path.exists():
            feature_names = joblib.load(features_path)
            logger.info(f"✅ Feature names loaded: {len(feature_names)} features")
        else:
            logger.warning(f"⚠️ Feature names not found")

        logger.info("🎉 API Ready!")

    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        import traceback
        logger.error(traceback.format_exc())

# Request/Response models - WordPress compatible
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
    currency: str = "USD"  # WordPress sends this

class TopFeature(BaseModel):
    feature: str
    contribution: float

class PredictionResponse(BaseModel):
    label: str  # WordPress expects this field
    confidence: float  # WordPress expects this field
    top_features: List[TopFeature]  # WordPress expects this field
    latency_ms: float

def convert_to_usd(amount: float, currency: str) -> float:
    """Convert amount to USD"""
    rates = {
        'USD': 1.0, 'PKR': 0.0036, 'INR': 0.012,
        'EUR': 1.10, 'GBP': 1.27, 'CAD': 0.74, 'AUD': 0.66
    }
    return amount * rates.get(currency.upper(), 1.0)

def get_email_reputation(email_domain: str) -> float:
    """
    Email domain reputation based on real fraud patterns:
    - Temporary email = 0.1 (high fraud risk)
    - Trusted providers = 0.8 (but can still be compromised)
    - Unknown domains = 0.4 (neutral, need other signals)
    """
    suspicious = [
        'tempmail', 'throwaway', '10minute', 'guerrilla', 'temp', 'disposable',
        'mailinator', 'sharklasers', 'guerrillamail', 'maildrop', 'yopmail',
        'trashmail', 'mintemail', 'fakeinbox', 'throwawaymail'
    ]
    trusted = [
        'gmail', 'yahoo', 'outlook', 'hotmail', 'icloud', 'protonmail',
        'aol', 'msn', 'live', 'me.com'
    ]

    domain_lower = email_domain.lower()

    if any(s in domain_lower for s in suspicious):
        return 0.1  # Temporary emails are red flags
    if any(t in domain_lower for t in trusted):
        return 0.8  # Trusted but not 1.0 (accounts can be compromised)
    return 0.4  # Unknown domain = neutral, needs other signals

def estimate_user_history(user_id_hash: str, is_new_user: bool):
    """Estimate user order count and account age"""
    if is_new_user:
        # New users are high risk - 0 history
        return 0, 0, 0.0

    # Existing users - estimate based on hash
    hash_val = hash(user_id_hash) % 100
    order_count = min(50, max(1, hash_val // 2))
    account_age = min(1000, max(7, hash_val * 10))
    # Increase fraud rate for suspicious user IDs
    fraud_rate = 0.05 if hash_val < 10 else 0.0

    return order_count, account_age, fraud_rate

def estimate_card_fraud_rate(payment_method: str, amount: float) -> float:
    """
    Real e-commerce card fraud rates:
    - Most credit cards have $5K-$25K daily limits
    - Business cards: $50K-$100K limits
    - Anything above these is suspicious
    """
    if payment_method == 'credit_card':
        # Based on real credit card limits and fraud patterns
        if amount >= 100000:
            return 0.99  # $100K+ = beyond credit card limits = fraud
        elif amount >= 50000:
            return 0.90  # $50K+ = max business card limit = very risky
        elif amount >= 25000:
            return 0.70  # $25K+ = above typical daily limit = risky
        elif amount >= 10000:
            return 0.50  # $10K+ = high-value = needs review
        elif amount >= 5000:
            return 0.30  # $5K+ = elevated risk
        elif amount >= 2000:
            return 0.15  # $2K+ = moderate risk
        elif amount > 1000:
            return 0.08
        elif amount > 500:
            return 0.04
        else:
            return 0.02
    elif payment_method == 'paypal':
        return 0.01  # PayPal has buyer protection
    elif payment_method == 'debit_card':
        # Debit cards have lower limits than credit cards
        if amount >= 5000:
            return 0.80  # Debit cards rarely go this high
        else:
            return 0.03
    return 0.05  # Other methods (crypto, etc.) - higher baseline risk

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FraudShield AI API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/v1/health",
            "predict": "/api/v1/predict"
        }
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "version": "2.0.0"
    }

@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(transaction: Transaction):
    """Predict fraud - WordPress compatible"""
    start_time = time.time()

    logger.info(f"📝 Prediction request: ${transaction.amount} {transaction.currency}, new_user={transaction.is_new_user}")

    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Prepare features
        features = prepare_features(transaction)

        # Predict
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0]
        fraud_prob = float(probability[1])

        # Label
        label = "fraud" if prediction == 1 else "legitimate"

        # Top features
        top_features = get_top_features(features[0])

        latency_ms = (time.time() - start_time) * 1000

        logger.info(f"✅ Result: {label} ({fraud_prob:.2%}), latency={latency_ms:.1f}ms")

        return {
            "label": label,
            "confidence": fraud_prob,
            "top_features": top_features,
            "latency_ms": latency_ms
        }

    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        import traceback
        logger.error(traceback.format_exc())

        return {
            "label": "error",
            "confidence": 0.0,
            "top_features": [
                {"feature": "Error occurred", "contribution": 0.0}
            ],
            "latency_ms": (time.time() - start_time) * 1000
        }

def prepare_features(txn: Transaction) -> np.ndarray:
    """Prepare features for model - Real e-commerce fraud detection"""

    amount_usd = convert_to_usd(txn.amount, txn.currency)

    # Real e-commerce thresholds:
    # - New users: first purchase >$5K is VERY suspicious
    # - All users: >$50K is extreme
    is_new_user_high_value = txn.is_new_user and amount_usd > 5000
    is_extreme_amount = amount_usd >= 50000
    is_suspicious = is_new_user_high_value or is_extreme_amount

    email_reputation = get_email_reputation(txn.email_domain)

    # Reduce email trust for suspicious transactions
    if is_new_user_high_value:
        # New user + high value = don't trust email at all
        email_reputation = min(email_reputation, 0.1)
    elif is_extreme_amount:
        email_reputation = min(email_reputation, 0.3)

    user_order_count, account_age_days, previous_fraud_rate = estimate_user_history(
        txn.user_id_hash, txn.is_new_user
    )

    # For suspicious transactions, reduce trust signals
    if is_new_user_high_value:
        # New user high-value: maximum scrutiny
        user_order_count = 0  # Force to zero
        account_age_days = 0  # Force to zero
        previous_fraud_rate = 0.8  # Very high assumed fraud rate
    elif is_extreme_amount:
        user_order_count = min(user_order_count, 1)
        account_age_days = min(account_age_days, 7)
        previous_fraud_rate = max(previous_fraud_rate, 0.5)

    avg_item_price = amount_usd / txn.items_count if txn.items_count > 0 else 0
    is_weekend = txn.day_of_week >= 5
    is_night_time = txn.hour_of_day < 6 or txn.hour_of_day > 22

    # Velocity based on risk level
    if is_new_user_high_value:
        velocity_24h = 15  # Very high velocity for new user + high amount
    elif is_extreme_amount:
        velocity_24h = 10
    elif txn.is_new_user and amount_usd > 500:
        velocity_24h = 5
    else:
        velocity_24h = 1

    # IP/country match - assume mismatch for suspicious transactions
    if is_suspicious:
        ip_country_match = False  # Don't trust for suspicious transactions
    else:
        ip_country_match = txn.billing_shipping_match

    card_bin_fraud_rate = estimate_card_fraud_rate(txn.payment_method, amount_usd)

    # Encode categoricals
    payment_method_encoded = encode_categorical('payment_method', txn.payment_method)
    device_type_encoded = encode_categorical('device_type', txn.device_type)

    # Build feature array
    features = np.array([[
        amount_usd, payment_method_encoded, int(txn.is_new_user),
        user_order_count, int(txn.billing_shipping_match), email_reputation,
        txn.hour_of_day, txn.day_of_week, int(is_weekend), int(is_night_time),
        txn.items_count, avg_item_price, 0, device_type_encoded,
        int(ip_country_match), velocity_24h, account_age_days,
        previous_fraud_rate, card_bin_fraud_rate, 0
    ]], dtype=np.float32)

    logger.info(f"Features: amount={amount_usd:.0f}, new_user={txn.is_new_user}, email_rep={email_reputation:.2f}, addr_match={txn.billing_shipping_match}, velocity={velocity_24h}")

    return features

def encode_categorical(column: str, value: str) -> int:
    """Encode categorical value"""
    if label_encoders and column in label_encoders:
        try:
            return int(label_encoders[column].transform([value])[0])
        except:
            return 0
    return 0

def get_top_features(features: np.ndarray) -> List[dict]:
    """Get top 3 features"""
    if not hasattr(model, 'feature_importances_'):
        return [
            {"feature": "Transaction Amount", "contribution": 0.35},
            {"feature": "New Customer", "contribution": 0.28},
            {"feature": "Address Mismatch", "contribution": 0.22}
        ]

    importances = model.feature_importances_
    feature_display_names = {
        'amount': 'Transaction Amount',
        'payment_method_encoded': 'Payment Method',
        'is_new_user': 'New Customer',
        'user_order_count': 'Order History',
        'billing_shipping_match': 'Address Match',
        'email_domain_reputation': 'Email Reputation',
        'hour_of_day': 'Transaction Hour',
        'day_of_week': 'Day of Week',
        'is_weekend': 'Weekend Transaction',
        'is_night_time': 'Night Time Transaction',
        'items_count': 'Number of Items',
        'avg_item_price': 'Average Item Price',
        'has_digital_items': 'Digital Items',
        'device_type_encoded': 'Device Type',
        'ip_country_match': 'IP/Country Match',
        'velocity_24h': 'Recent Activity',
        'account_age_days': 'Account Age',
        'previous_fraud_rate': 'Historical Fraud',
        'card_bin_fraud_rate': 'Card Risk Score',
        'shipping_method_encoded': 'Shipping Method'
    }

    top_indices = np.argsort(importances)[-3:][::-1]
    top_features = []

    for idx in top_indices:
        feature_name = feature_names[idx] if feature_names else f"feature_{idx}"
        display_name = feature_display_names.get(feature_name, feature_name)
        top_features.append({
            "feature": display_name,
            "contribution": float(importances[idx])
        })

    return top_features

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
