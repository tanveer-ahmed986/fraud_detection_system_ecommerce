# Data Model

## Entity Relationship

```
transactions 1──1 predictions
models (standalone, version-tracked)
audit_entries (append-only log)
merchant_configs (per-merchant settings)
```

## Table: transactions
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Transaction identifier |
| merchant_id | VARCHAR(100) | NOT NULL, indexed | Merchant identifier |
| amount | FLOAT | NOT NULL, CHECK >0 | Transaction amount |
| payment_method | VARCHAR(50) | NOT NULL | credit_card, debit_card, paypal, crypto, bank_transfer |
| user_id_hash | VARCHAR(64) | NOT NULL | SHA-256 hash of user ID (no raw PII) |
| ip_hash | VARCHAR(64) | NOT NULL | SHA-256 hash of IP address |
| email_domain | VARCHAR(100) | NOT NULL | Domain only (e.g., gmail.com) |
| is_new_user | BOOLEAN | NOT NULL, default false | First-time buyer flag |
| device_type | VARCHAR(30) | NOT NULL | desktop, mobile, tablet |
| billing_shipping_match | BOOLEAN | NOT NULL, default true | Address match flag |
| hour_of_day | INTEGER | NOT NULL, CHECK 0-23 | Hour of transaction |
| day_of_week | INTEGER | NOT NULL, CHECK 0-6 | Day (0=Monday) |
| items_count | INTEGER | NOT NULL, CHECK ≥1 | Number of items |
| created_at | TIMESTAMP | NOT NULL, default now | Creation timestamp |

## Table: predictions
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Prediction identifier |
| transaction_id | UUID | FK→transactions.id, UNIQUE | Linked transaction |
| model_version | VARCHAR(20) | NOT NULL | Model version used |
| label | VARCHAR(15) | NOT NULL | "fraud" or "legitimate" |
| confidence | FLOAT | NOT NULL, CHECK 0-1 | Fraud probability |
| threshold_used | FLOAT | NOT NULL | Decision threshold |
| feature_contributions | JSONB | NOT NULL | Top-3 SHAP contributions |
| latency_ms | FLOAT | NOT NULL | Inference latency |
| fallback_applied | BOOLEAN | NOT NULL, default false | Fallback flag |
| created_at | TIMESTAMP | NOT NULL, default now | Creation timestamp |

## Table: models
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Auto-increment ID |
| version | VARCHAR(20) | NOT NULL, UNIQUE | Semantic version |
| file_path | VARCHAR(255) | NOT NULL | Path to .joblib file |
| sha256_hash | VARCHAR(64) | NOT NULL | Integrity hash |
| is_active | BOOLEAN | NOT NULL, default false | Currently serving |
| recall | FLOAT | | Model recall |
| precision | FLOAT | | Model precision |
| f1_score | FLOAT | | F1 score |
| fpr | FLOAT | | False positive rate |
| dataset_rows | INTEGER | | Training data size |
| dataset_fraud_pct | FLOAT | | Fraud percentage |
| training_duration_s | FLOAT | | Training time |
| created_at | TIMESTAMP | NOT NULL, default now | Creation timestamp |

## Table: audit_entries
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PK | Auto-increment ID |
| event_type | VARCHAR(30) | NOT NULL, indexed | prediction/training/rollback/config_change/fallback |
| event_data | JSONB | NOT NULL | Full event context |
| model_version | VARCHAR(20) | | Model version (if applicable) |
| created_at | TIMESTAMP | NOT NULL, indexed | Event timestamp |

## Table: merchant_configs
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| merchant_id | VARCHAR(100) | PK | Merchant identifier |
| api_endpoint | VARCHAR(500) | | Callback URL |
| fraud_threshold | FLOAT | NOT NULL, default 0.50 | Custom threshold |
| fallback_amount_limit | FLOAT | NOT NULL, default 50.00 | Fallback cutoff |
| notifications_enabled | BOOLEAN | NOT NULL, default true | Email alerts |
| api_key_hash | VARCHAR(64) | | Hashed API key |
| updated_at | TIMESTAMP | NOT NULL | Last update |

## Indexes
- `transactions.merchant_id` — filter by merchant
- `audit_entries.event_type` — filter audit log
- `audit_entries.created_at` — date range queries
- `models.version` — unique constraint
- `predictions.transaction_id` — unique constraint (1:1)
