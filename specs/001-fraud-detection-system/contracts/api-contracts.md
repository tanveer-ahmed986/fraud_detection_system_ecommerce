# API Contract: POST /api/v1/predict

## Request
```
POST /api/v1/predict
Content-Type: application/json
```

### Body
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| merchant_id | string | yes | max 100 chars |
| amount | float | yes | > 0 |
| payment_method | string | yes | max 50 chars |
| user_id_hash | string | yes | max 64 chars |
| ip_hash | string | yes | max 64 chars |
| email_domain | string | yes | max 100 chars |
| is_new_user | boolean | no | default: false |
| device_type | string | yes | max 30 chars |
| billing_shipping_match | boolean | no | default: true |
| hour_of_day | integer | yes | 0-23 |
| day_of_week | integer | yes | 0-6 |
| items_count | integer | no | default: 1, ≥1 |

### Response 200
```json
{
  "transaction_id": "uuid",
  "label": "fraud | legitimate",
  "confidence": 0.0-1.0,
  "threshold_used": 0.5,
  "top_features": [
    {"feature": "string", "contribution": float}
  ],
  "latency_ms": float,
  "fallback_applied": boolean
}
```

### Response 422 — Validation Error
### Response 429 — Rate Limit (100 req/s)
### Response 500 — Model unavailable (fallback applies)

---

# API Contract: POST /api/v1/retrain

## Request
```
POST /api/v1/retrain
Content-Type: application/json
X-API-Key: <api-key>
```

### Body
| Field | Type | Required | Default |
|-------|------|----------|---------|
| dataset_path | string | no | data/demo_transactions.csv |
| min_recall | float | no | 0.90 |
| max_fpr | float | no | 0.05 |

### Response 200
```json
{
  "version": "2.0",
  "recall": 0.92,
  "precision": 0.88,
  "f1_score": 0.90,
  "fpr": 0.04,
  "dataset_rows": 5000,
  "dataset_fraud_pct": 5.0,
  "training_duration_s": 2.5,
  "promoted": true,
  "message": "All metric gates passed"
}
```

### Response 403 — Invalid API key

---

# API Contract: GET /api/v1/health

### Response 200
```json
{
  "status": "healthy | degraded",
  "model_loaded": boolean,
  "model_version": "string"
}
```

---

# API Contract: GET /api/v1/audit

### Query Parameters
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| event_type | string | null | Filter by type |
| start_date | datetime | null | Start filter |
| end_date | datetime | null | End filter |
| page | int | 1 | Page number |
| page_size | int | 50 | Items per page (max 200) |

### Response 200
```json
{
  "total": int,
  "page": int,
  "page_size": int,
  "entries": [
    {
      "id": int,
      "event_type": "string",
      "event_data": {},
      "model_version": "string | null",
      "created_at": "ISO datetime"
    }
  ]
}
```

---

# API Contract: GET /api/v1/models

### Response 200
```json
[
  {
    "version": "string",
    "is_active": boolean,
    "recall": float,
    "precision": float,
    "f1_score": float,
    "fpr": float,
    "dataset_rows": int,
    "created_at": "ISO datetime"
  }
]
```

---

# API Contract: POST /api/v1/models/{version}/activate

```
X-API-Key: <api-key>
```

### Response 200
```json
{
  "message": "Model {version} activated",
  "version": "string"
}
```

### Response 403 — Invalid API key
### Response 404 — Version not found

---

# API Contract: GET /api/v1/dashboard/summary

### Response 200
```json
{
  "total_predictions": int,
  "fraud_count": int,
  "legitimate_count": int,
  "fraud_rate": float,
  "avg_confidence": float,
  "model_version": "string",
  "model_recall": float | null,
  "model_precision": float | null,
  "model_fpr": float | null
}
```

---

# API Contract: GET /api/v1/dashboard/timeseries

### Query: `days` (int, default 30)

### Response 200
```json
[
  {"date": "YYYY-MM-DD", "total": int, "fraud": int, "fraud_rate": float}
]
```

---

# API Contract: GET /api/v1/dashboard/predictions

### Query: `page`, `page_size`, `label` (optional filter)

### Response 200
```json
{
  "total": int,
  "page": int,
  "page_size": int,
  "predictions": [
    {
      "transaction_id": "uuid",
      "amount": float,
      "label": "string",
      "confidence": float,
      "merchant_id": "string",
      "created_at": "ISO datetime",
      "top_features": [{"feature": "string", "contribution": float}]
    }
  ]
}
```
