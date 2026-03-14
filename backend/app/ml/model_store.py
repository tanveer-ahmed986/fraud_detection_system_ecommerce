import hashlib
import os
import joblib
from pathlib import Path
from typing import Any


def compute_sha256(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def save_model(model: Any, model_dir: str, version: str) -> tuple[str, str]:
    """Save model and return (file_path, sha256_hash)."""
    os.makedirs(model_dir, exist_ok=True)
    file_path = os.path.join(model_dir, f"v{version}.joblib")
    joblib.dump(model, file_path)
    sha256 = compute_sha256(file_path)
    return file_path, sha256


def load_model(file_path: str, expected_hash: str | None = None) -> Any:
    """Load model with optional SHA-256 integrity check."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Model file not found: {file_path}")

    if expected_hash:
        actual_hash = compute_sha256(file_path)
        if actual_hash != expected_hash:
            raise ValueError(
                f"Model integrity check failed. Expected {expected_hash}, got {actual_hash}"
            )

    return joblib.load(file_path)
