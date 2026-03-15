"""
Quick script to save the creditcard model with optimized threshold
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import pickle
import json
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score, precision_score, f1_score, confusion_matrix
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import shap
import joblib

print("Training creditcard model with optimized threshold...")

# Load data
df = pd.read_csv('/creditcard.csv')
X = df.drop(['Class'], axis=1)
y = df['Class']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# SMOTE
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# Train
model = xgb.XGBClassifier(
    objective='binary:logistic',
    eval_metric='auc',
    max_depth=6,
    learning_rate=0.1,
    n_estimators=200,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    tree_method='hist'
)

print("Training...")
model.fit(X_train_balanced, y_train_balanced)
print("✓ Training complete")

# Find optimal threshold
y_pred_proba = model.predict_proba(X_test)[:, 1]

best_threshold = 0.4
best_score = 0

for threshold in [0.3, 0.35, 0.4, 0.45, 0.5]:
    y_pred = (y_pred_proba >= threshold).astype(int)
    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"Threshold {threshold}: Recall={recall:.3f}, Precision={precision:.3f}, F1={f1:.3f}")

    if recall >= 0.85 and precision >= 0.65:
        if f1 > best_score:
            best_score = f1
            best_threshold = threshold

# Evaluate with best threshold
y_pred = (y_pred_proba >= best_threshold).astype(int)
recall = recall_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
fpr = fp / (fp + tn)

print(f"\n✓ Optimal threshold: {best_threshold}")
print(f"  Recall: {recall:.4f}")
print(f"  Precision: {precision:.4f}")
print(f"  F1: {f1:.4f}")
print(f"  FPR: {fpr:.6f}")
print(f"  TP={tp}, FP={fp}, TN={tn}, FN={fn}")

# Create SHAP explainer
print("\nCreating SHAP explainer...")
explainer = shap.TreeExplainer(model)
print("✓ SHAP explainer created")

# Save model
models_dir = Path('/app/models')
models_dir.mkdir(exist_ok=True)

# Save as joblib (compatible with endpoint)
model_path = models_dir / 'creditcard_model.joblib'
joblib.dump(model, model_path)
print(f"✓ Model saved: {model_path}")

explainer_path = models_dir / 'creditcard_explainer.joblib'
joblib.dump(explainer, explainer_path)
print(f"✓ Explainer saved: {explainer_path}")

# Save metadata
metadata = {
    'version': 'creditcard_v2.0',
    'created_at': datetime.now().isoformat(),
    'model_type': 'XGBoost',
    'dataset': 'creditcard.csv',
    'dataset_size': len(df),
    'fraud_count': int(y.sum()),
    'fraud_percentage': float(y.mean() * 100),
    'optimal_threshold': best_threshold,
    'metrics': {
        'recall': float(recall),
        'precision': float(precision),
        'f1_score': float(f1),
        'fpr': float(fpr)
    },
    'confusion_matrix': {
        'tp': int(tp),
        'fp': int(fp),
        'tn': int(tn),
        'fn': int(fn)
    },
    'training_config': {
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 200,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'used_smote': True
    }
}

metadata_path = models_dir / 'creditcard_metadata.json'
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"✓ Metadata saved: {metadata_path}")

print("\n✓ Model ready for use!")
print(f"\nTest with: curl -X POST http://localhost:8000/api/v1/predict/creditcard -F 'file=@creditcard_sample.csv'")
