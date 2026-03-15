"""
Batch prediction endpoint specifically for creditcard.csv format
Handles Kaggle Credit Card Fraud Detection dataset format (V1-V28 features)
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import numpy as np
import io
import uuid
from datetime import datetime

from app.dependencies import get_db
from app.models.db import Transaction, Prediction, AuditEntry

router = APIRouter(prefix="/api/v1", tags=["creditcard"])


@router.post("/predict/creditcard")
async def creditcard_batch_predict(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload creditcard.csv format file and get batch predictions.

    CSV Format (Kaggle Credit Card Fraud Detection):
    Time,V1,V2,V3,...,V28,Amount,Class (optional)

    Returns JSON with all predictions.
    """
    from app.main import app_state
    from sklearn.preprocessing import StandardScaler
    import joblib

    # Check if we have a creditcard-trained model
    try:
        # Try to load creditcard-specific model
        model_path = "models/creditcard_model.joblib"
        explainer_path = "models/creditcard_explainer.joblib"

        import os
        if not os.path.exists(model_path):
            raise HTTPException(
                status_code=503,
                detail="Creditcard model not found. Please train a model on creditcard.csv first using: python scripts/train_on_creditcard.py"
            )

        model = joblib.load(model_path)
        try:
            explainer = joblib.load(explainer_path)
        except:
            explainer = None

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to load creditcard model: {str(e)}"
        )

    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        # Read CSV content
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))

        # Expected columns for creditcard.csv
        expected_v_cols = [f'V{i}' for i in range(1, 29)]  # V1 to V28
        required_cols = ['Time', 'Amount'] + expected_v_cols

        # Check if we have the required creditcard.csv columns
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid creditcard.csv format. Missing columns: {', '.join(missing_cols)}. "
                       f"Expected format: Time, V1-V28, Amount, Class (optional)"
            )

        # Check if Class column exists (ground truth)
        has_labels = 'Class' in df.columns

        # Prepare features in correct order
        feature_cols = ['Time'] + expected_v_cols + ['Amount']
        X = df[feature_cols].copy()

        # Get predictions
        y_pred_proba = model.predict_proba(X)[:, 1]  # Probability of fraud

        # Use optimal threshold from metadata or default
        try:
            import json
            with open('models/v2.0_metadata.json', 'r') as f:
                metadata = json.load(f)
                threshold = metadata.get('optimal_threshold', 0.4)
        except:
            threshold = 0.4  # Default for creditcard model

        y_pred = (y_pred_proba >= threshold).astype(int)

        # Process each transaction
        results = []
        for idx, row in df.iterrows():
            txn_id = uuid.uuid4()
            confidence = float(y_pred_proba[idx])
            predicted_label = "fraud" if y_pred[idx] == 1 else "legitimate"

            # Get actual label if available
            actual_label = None
            if has_labels:
                actual_label = "fraud" if row['Class'] == 1 else "legitimate"

            # Get top features (SHAP values if available)
            top_features = []
            if explainer is not None:
                try:
                    shap_values = explainer.shap_values(X.iloc[idx:idx+1])
                    feature_importance = list(zip(feature_cols, shap_values[0]))
                    feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
                    top_features = [
                        {"feature": feat, "contribution": float(val)}
                        for feat, val in feature_importance[:3]
                    ]
                except:
                    # Fallback: use raw feature values
                    top_features = [
                        {"feature": "Amount", "contribution": float(row['Amount'])},
                        {"feature": "V1", "contribution": float(row['V1'])},
                        {"feature": "V2", "contribution": float(row['V2'])}
                    ]

            # Create minimal transaction record (using creditcard data as-is)
            txn = Transaction(
                id=txn_id,
                merchant_id=f"CC_{idx}",  # Placeholder
                amount=max(0.01, float(row['Amount'])),  # DB requires positive amount
                payment_method="credit_card",
                user_id_hash=f"user_{idx}",
                ip_hash=f"ip_{idx}",
                email_domain="creditcard.csv",
                is_new_user=False,
                device_type="unknown",
                billing_shipping_match=True,
                hour_of_day=int(row['Time'] // 3600 % 24),  # Convert seconds to hour
                day_of_week=0,
                items_count=1,
            )
            db.add(txn)

            # Save prediction
            pred = Prediction(
                id=uuid.uuid4(),
                transaction_id=txn_id,
                model_version="creditcard_v2.0",
                label=predicted_label,
                confidence=confidence,
                threshold_used=threshold,
                feature_contributions=top_features,
                latency_ms=0.0,  # Batch processing
                fallback_applied=False,
            )
            db.add(pred)

            # Audit log
            audit = AuditEntry(
                event_type='creditcard_batch_prediction',
                event_data={
                    'transaction_id': str(txn_id),
                    'amount': float(row['Amount']),
                    'predicted_label': predicted_label,
                    'confidence': confidence,
                    'actual_label': actual_label,
                    'batch_index': idx
                },
                model_version="creditcard_v2.0",
            )
            db.add(audit)

            # Build response
            result = {
                'transaction_id': str(txn_id),
                'row_index': idx,
                'amount': round(float(row['Amount']), 2),
                'time': float(row['Time']),
                'predicted_label': predicted_label,
                'confidence': round(confidence, 4),
                'threshold_used': threshold,
                'top_features': top_features,
            }

            if has_labels:
                result['actual_label'] = actual_label
                result['correct'] = (predicted_label == actual_label)

            results.append(result)

        # Commit all at once
        await db.commit()

        # Calculate summary stats
        fraud_predicted = sum(1 for r in results if r['predicted_label'] == 'fraud')
        fraud_actual = sum(1 for r in results if r.get('actual_label') == 'fraud') if has_labels else None

        # Calculate accuracy if we have labels
        accuracy = None
        if has_labels:
            correct = sum(1 for r in results if r.get('correct', False))
            accuracy = round(correct / len(results) * 100, 2)

        response = {
            'success': True,
            'total_transactions': len(results),
            'fraud_predicted': fraud_predicted,
            'legitimate_predicted': len(results) - fraud_predicted,
            'fraud_rate_predicted': round(fraud_predicted / len(results) * 100, 2) if results else 0,
            'threshold_used': threshold,
            'model_version': 'creditcard_v2.0',
            'predictions': results
        }

        if has_labels:
            response['fraud_actual'] = fraud_actual
            response['accuracy'] = accuracy
            response['has_ground_truth'] = True

        return response

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding error. Please use UTF-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
