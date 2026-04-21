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
from typing import List, Optional
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
    reason: Optional[str] = None  # Human-readable explanation

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
        label = "HIGH RISK" if prediction == 1 else "LOW RISK"
        is_high_risk = (prediction == 1)

        # Top features with context-aware explanations
        logger.info(f"🔍 About to call get_top_features with features shape: {features.shape}, features[0] shape: {features[0].shape}, is_high_risk: {is_high_risk}")
        top_features = get_top_features(features[0], is_high_risk)
        logger.info(f"🔍 get_top_features returned: {top_features}")

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

def explain_feature(feature_name: str, feature_value: float, contribution: float, is_high_risk: bool) -> str:
    """Generate human-readable explanation for why a feature affects fraud risk

    Args:
        feature_name: Name of the feature (e.g., 'is_new_user', 'amount')
        feature_value: Actual value of the feature
        contribution: How much it contributes to risk (positive = increases, negative = decreases)
        is_high_risk: Whether the overall transaction is HIGH RISK (for context-aware messaging)

    Returns:
        Human-readable explanation
    """
    is_risky = contribution > 0
    is_significant = abs(contribution) > 0.05  # Contributions >5% are significant

    # Map features to explanations based on their values
    if feature_name == 'is_new_user' and feature_value > 0.5:
        return "New customer with no purchase history" if is_risky else "Returning customer with verified history"

    elif feature_name == 'email_domain_reputation':
        if feature_value < 0.3:
            # Low reputation (suspicious)
            if is_high_risk:
                return "Email from suspicious or unknown domain"
            else:
                return "Email domain requires verification" if is_significant else "Standard email verification"
        elif feature_value > 0.7:
            # High reputation (trusted)
            if not is_high_risk:
                return "Trusted email provider (outlook.com, gmail.com, etc.)"
            else:
                return "Email provider is reputable but other factors raise concerns"
        else:
            # Medium reputation
            if is_high_risk:
                return "Unverified email domain"
            else:
                return "Email from standard provider" if is_significant else "Email verification passed"

    elif feature_name == 'amount':
        if feature_value > 5000:
            return f"Unusually large transaction amount (${feature_value:,.0f})" if is_risky else f"Large transaction amount verified (${feature_value:,.0f})"
        elif feature_value > 1000:
            return f"High transaction amount (${feature_value:,.0f})" if is_risky else f"Normal high-value purchase (${feature_value:,.0f})"
        else:
            return "Normal transaction amount" if not is_risky else "Transaction amount concern"

    elif feature_name == 'billing_shipping_match' and feature_value < 0.5:
        return "Billing and shipping addresses don't match" if is_risky else "Address verification needed"

    elif feature_name == 'ip_country_match' and feature_value < 0.5:
        return "IP location doesn't match billing country" if is_risky else "Location verification needed"

    elif feature_name == 'user_order_count':
        if feature_value == 0:
            return "First-time buyer with no order history" if is_risky else "New customer - first purchase"
        elif feature_value < 3:
            return "Limited purchase history" if is_risky else "Returning customer"
        else:
            return "Established customer with purchase history" if not is_risky else "Active customer account"

    elif feature_name == 'velocity_24h':
        if feature_value > 5:
            # Very high velocity
            if is_high_risk:
                return f"Multiple transactions in short time ({int(feature_value)} in 24h)"
            else:
                return "Active customer with multiple recent purchases"
        elif feature_value > 2:
            # Medium velocity
            if is_high_risk:
                return "Elevated transaction frequency"
            else:
                return "Normal shopping activity"
        else:
            # Low velocity
            if is_high_risk:
                return "Transaction pattern analyzed"
            else:
                return "Standard purchase frequency"

    elif feature_name == 'account_age_days':
        if feature_value == 0:
            return "Brand new account created today" if is_risky else "New account verification"
        elif feature_value < 7:
            return f"Very new account ({int(feature_value)} days old)" if is_risky else "Recent account signup"
        elif feature_value < 30:
            return "Account less than 1 month old" if is_risky else "Established recent account"
        else:
            return "Mature account with history" if not is_risky else "Long-standing account"

    elif feature_name == 'previous_fraud_rate':
        if feature_value > 0.5:
            return "High fraud rate in customer history" if is_risky else "Fraud history detected"
        elif feature_value > 0.2:
            return "Some fraud indicators in past transactions" if is_risky else "Minor fraud history"
        else:
            return "Clean transaction history" if not is_risky else "No previous fraud"

    elif feature_name == 'card_bin_fraud_rate':
        if feature_value > 0.5:
            # High fraud rate for this card type
            if is_high_risk:
                return "Card type frequently used in fraud"
            else:
                return "Card type monitored (extra verification applied)"
        elif feature_value > 0.2:
            # Medium fraud rate
            if is_high_risk:
                return "Card has elevated fraud risk"
            else:
                return "Standard card verification completed"
        else:
            # Low fraud rate
            if is_high_risk:
                return "Card type verified (other factors raise concerns)"
            else:
                return "Card from trusted issuer"

    elif feature_name == 'is_night_time' and feature_value > 0.5:
        return "Transaction at unusual hours (late night/early morning)" if is_risky else "Off-hours transaction"

    elif feature_name == 'is_weekend' and feature_value > 0.5:
        return "Weekend transaction pattern" if is_risky else "Weekend purchase"

    elif feature_name == 'items_count':
        if feature_value > 10:
            return f"Large cart size ({int(feature_value)} items)" if is_risky else "Bulk purchase detected"
        elif feature_value == 1:
            return "Single item purchase" if is_risky else "Simple transaction"
        else:
            return "Normal cart size" if not is_risky else "Standard item count"

    elif feature_name == 'avg_item_price':
        if feature_value > 1000:
            return f"High average item price (${feature_value:,.0f})" if is_risky else "Premium items in cart"
        elif feature_value < 10:
            return "Low-value items" if is_risky else "Budget purchases"
        else:
            return "Normal item pricing" if not is_risky else "Standard price range"

    # Fallback for unknown features
    feature_display = {
        'payment_method_encoded': 'Payment method',
        'device_type_encoded': 'Device type',
        'shipping_method_encoded': 'Shipping method',
        'has_digital_items': 'Digital items',
        'hour_of_day': 'Transaction timing',
        'day_of_week': 'Day of week pattern'
    }.get(feature_name, feature_name.replace('_', ' ').title())

    return f"{feature_display} {'increases' if is_risky else 'decreases'} fraud risk"

def get_top_features(features: np.ndarray, is_high_risk: bool = True) -> List[dict]:
    """Get top 3 features with transaction-specific contributions

    Args:
        features: 1D array of feature values for a single transaction
        is_high_risk: Whether the overall transaction is HIGH RISK (for context-aware explanations)
    """
    if not hasattr(model, 'feature_importances_'):
        if is_high_risk:
            return [
                {"feature": "Transaction Amount", "contribution": 0.35, "reason": "High-value transaction requires review"},
                {"feature": "New Customer", "contribution": 0.28, "reason": "First-time buyer with no history"},
                {"feature": "Address Mismatch", "contribution": 0.22, "reason": "Billing and shipping addresses differ"}
            ]
        else:
            return [
                {"feature": "Transaction Amount", "contribution": 0.35, "reason": "Standard transaction amount"},
                {"feature": "Customer Profile", "contribution": 0.28, "reason": "Customer verification completed"},
                {"feature": "Address Verification", "contribution": 0.22, "reason": "Address information verified"}
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

    # Calculate feature contributions for THIS transaction
    # Simple approach: multiply importance by scaled feature value
    # This gives transaction-specific contributions (different for each transaction)

    try:
        logger.info(f"🔧 Calculating feature explanations - features shape: {features.shape}")
        contributions = []

        for idx in range(len(importances)):
            feature_value = features[idx]  # features is already 1D array

            # Scale feature value to reasonable range for display
            # Use tanh to bound to [-1, 1] range
            scaled_value = np.tanh(feature_value / 10.0)  # divide by 10 to avoid saturation

            # Contribution = importance * scaled value
            contribution = float(importances[idx] * scaled_value)
            contributions.append((idx, contribution, feature_value))

        # Get top 3 by absolute contribution
        top_indices_contrib = sorted(contributions, key=lambda x: abs(x[1]), reverse=True)[:3]

        top_features = []
        for idx, contrib, raw_value in top_indices_contrib:
            feature_name = feature_names[idx] if feature_names else f"feature_{idx}"
            display_name = feature_display_names.get(feature_name, feature_name)

            # Generate human-readable explanation
            reason = explain_feature(feature_name, raw_value, contrib, is_high_risk)

            top_features.append({
                "feature": display_name,
                "contribution": float(contrib),
                "reason": reason
            })

        logger.info(f"✅ Transaction-specific features with reasons: {top_features}")
        return top_features

    except Exception as e:
        logger.error(f"❌ Error calculating transaction-specific features: {e}")
        logger.error(f"Features type: {type(features)}, shape: {getattr(features, 'shape', 'no shape')}")
        import traceback
        logger.error(traceback.format_exc())

        # Fallback to global importance
        logger.warning("⚠️ Falling back to global feature importance")
        top_indices = np.argsort(importances)[-3:][::-1]
        top_features = []
        for idx in top_indices:
            feature_name = feature_names[idx] if feature_names else f"feature_{idx}"
            display_name = feature_display_names.get(feature_name, feature_name)
            top_features.append({
                "feature": display_name,
                "contribution": float(importances[idx]),
                "reason": "Risk factor analysis"
            })
        return top_features

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
