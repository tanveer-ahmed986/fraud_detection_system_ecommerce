# Quickstart Guide

Get from `git clone` to a live fraud prediction in under 5 minutes.

## Prerequisites
- Docker & Docker Compose
- Git
- curl (for testing)

## Steps

### 1. Clone and start (2 minutes)
```bash
git clone <repo-url> fraud_detection_system
cd fraud_detection_system
docker compose up --build -d
```

### 2. Wait for services (30 seconds)
```bash
# Check all services are running
docker compose ps

# Wait for backend to be ready
curl -s http://localhost:8000/api/v1/health
# Expected: {"status":"healthy","model_loaded":true,"model_version":"1.0"}
```

### 3. Seed data & train model (first run only)
The backend auto-creates tables and loads the seed model on first start.

If you need to re-seed:
```bash
docker compose exec backend python -m app.seed
```

### 4. Make a prediction (10 seconds)
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "shop_123",
    "amount": 299.99,
    "payment_method": "credit_card",
    "user_id_hash": "a1b2c3d4",
    "ip_hash": "e5f6g7h8",
    "email_domain": "gmail.com",
    "is_new_user": false,
    "device_type": "desktop",
    "billing_shipping_match": true,
    "hour_of_day": 14,
    "day_of_week": 2,
    "items_count": 3
  }'
```

Expected response:
```json
{
  "transaction_id": "uuid-here",
  "label": "legitimate",
  "confidence": 0.12,
  "threshold_used": 0.5,
  "top_features": [
    {"feature": "amount", "contribution": 0.08},
    {"feature": "is_new_user", "contribution": -0.05},
    {"feature": "hour_sin", "contribution": 0.03}
  ],
  "latency_ms": 8.5,
  "fallback_applied": false
}
```

### 5. Open the dashboard (5 seconds)
Navigate to **http://localhost:3000** in your browser.

You'll see:
- Fraud rate metrics cards
- Fraud rate over time chart
- Recent predictions table with drill-down

### 6. Try a suspicious transaction
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "shop_123",
    "amount": 4500.00,
    "payment_method": "crypto",
    "user_id_hash": "suspicious_user",
    "ip_hash": "suspicious_ip",
    "email_domain": "tempmail.org",
    "is_new_user": true,
    "device_type": "mobile",
    "billing_shipping_match": false,
    "hour_of_day": 3,
    "day_of_week": 6,
    "items_count": 1
  }'
```

### 7. View audit log
```bash
curl http://localhost:8000/api/v1/audit?page=1&page_size=10
```

### 8. Retrain model
```bash
curl -X POST http://localhost:8000/api/v1/retrain \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-api-key" \
  -d '{"min_recall": 0.90, "max_fpr": 0.05}'
```

## Stopping
```bash
docker compose down        # Stop services
docker compose down -v     # Stop and delete data
```

## Ports
| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Dashboard | 3000 | http://localhost:3000 |
| PostgreSQL | 5432 | localhost:5432 |
