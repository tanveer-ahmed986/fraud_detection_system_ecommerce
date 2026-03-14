#!/bin/bash
set -e

# Seed on first run (if no model exists)
if [ ! -f /app/models/v1.0.joblib ]; then
    echo "First run detected — seeding data and training initial model..."
    python -m app.seed
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
