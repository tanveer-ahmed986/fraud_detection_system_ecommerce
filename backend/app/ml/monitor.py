import logging
from sklearn.metrics import recall_score, confusion_matrix
import numpy as np

logger = logging.getLogger(__name__)


def check_drift(
    model,
    X: np.ndarray,
    y: np.ndarray,
    recall_threshold: float = 0.85,
    fpr_threshold: float = 0.07,
) -> dict:
    """Evaluate model on recent data and check for drift."""
    y_pred = model.predict(X)
    tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()

    recall = recall_score(y, y_pred)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    alerts = []
    if recall < recall_threshold:
        alerts.append(f"Recall dropped to {recall:.4f} (threshold: {recall_threshold})")
    if fpr > fpr_threshold:
        alerts.append(f"FPR rose to {fpr:.4f} (threshold: {fpr_threshold})")

    if alerts:
        for alert in alerts:
            logger.warning(f"DRIFT ALERT: {alert}")

    return {
        "recall": round(recall, 4),
        "fpr": round(fpr, 4),
        "alerts": alerts,
        "drifted": len(alerts) > 0,
    }
