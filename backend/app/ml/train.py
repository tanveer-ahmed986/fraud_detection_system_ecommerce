import time
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score, precision_score, f1_score, confusion_matrix


def train_model(
    X: np.ndarray,
    y: np.ndarray,
    random_state: int = 42,
) -> tuple[RandomForestClassifier, dict]:
    """Train a RandomForest and return (model, metrics_dict)."""
    start = time.time()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    duration = time.time() - start

    metrics = {
        "recall": round(recall, 4),
        "precision": round(precision, 4),
        "f1_score": round(f1, 4),
        "fpr": round(fpr, 4),
        "dataset_rows": len(X),
        "dataset_fraud_pct": round(float(y.mean()) * 100, 2),
        "training_duration_s": round(duration, 2),
    }

    return clf, metrics


def check_metric_gates(metrics: dict, min_recall: float = 0.90, max_fpr: float = 0.05) -> tuple[bool, str]:
    """Check if metrics pass promotion gates. Returns (passed, message)."""
    issues = []
    if metrics["recall"] < min_recall:
        issues.append(f"recall {metrics['recall']:.4f} < {min_recall}")
    if metrics["fpr"] > max_fpr:
        issues.append(f"FPR {metrics['fpr']:.4f} > {max_fpr}")

    if issues:
        return False, f"Metric gates failed: {', '.join(issues)}"
    return True, "All metric gates passed"
