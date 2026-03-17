# 🛡️ AI-Powered Fraud Detection System for E-commerce

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

A **production-ready, portfolio-grade** fraud detection system that protects e-commerce transactions using machine learning. Features real-time predictions, explainable AI, comprehensive analytics dashboard, and seamless WooCommerce integration.

---

## 🚀 Quick Start - WooCommerce Plugin

**Protect your WooCommerce store in 5 minutes:**

[![Download WooCommerce Plugin](https://img.shields.io/badge/Download-WooCommerce%20Plugin%20v2.2.1-blue?style=for-the-badge&logo=wordpress)](https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/releases/download/v2.2.1/wc-fraud-detection-v2.2.1-FIXED.zip)
[![Download PDF Manual](https://img.shields.io/badge/Download-PDF%20Manual-red?style=for-the-badge&logo=adobe)](https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/releases/download/v2.2.1/AI_Fraud_Detection_User_Manual_v2.2.1.pdf)

### New in v2.2.1:
- ✨ **CSV Bulk Upload** - Check hundreds of transactions at once
- ✨ **Manual Check Button** - On-demand fraud analysis for any order
- ✨ **Real-time Progress** - Track processing with progress bars
- ✨ **Results Export** - Download fraud reports as CSV
- 🐛 **Bug Fixes** - Improved CSV parsing and error messages

### Installation:
1. Download the plugin above
2. Upload to WordPress (Plugins → Add New → Upload)
3. Configure API endpoint at WooCommerce → Fraud Detection
4. Done! Real-time fraud detection is active ✅

**Requirements:** WordPress 5.8+, WooCommerce 8.0+, PHP 7.4+

[📖 Full Installation Guide](woocommerce-plugin/INSTALL.md) | [📄 User Manual](woocommerce-plugin/USER_MANUAL.md) | [🚀 Quick Start](woocommerce-plugin/00-START-HERE.md) | [📋 Release Notes](woocommerce-plugin/RELEASE_NOTES_v2.2.1.md)

---

![Dashboard Preview](docs/dashboard-preview.png)

---

## 🌟 Key Features

### 🎯 Core Capabilities
- **⚡ Real-time Fraud Detection** - Sub-200ms prediction latency (p95)
- **🔍 Explainable AI** - SHAP values show top contributing features for every prediction
- **📊 Analytics Dashboard** - Beautiful React UI with fraud trends, model metrics, and transaction drill-down
- **🔐 Audit Logging** - Complete compliance trail for GDPR, PCI-DSS requirements
- **🛒 WooCommerce Plugin** - Drop-in PHP plugin for instant integration
- **📈 Model Management** - Versioning, retraining, rollback, and A/B testing support

### 🎓 Machine Learning
- **Algorithm**: XGBoost Classifier (optimized for imbalanced data)
- **Performance**: Recall ≥90%, Precision ≥85%, False Positive Rate ≤5%
- **Interpretability**: SHAP (SHapley Additive exPlanations) for every prediction
- **Monitoring**: Automated drift detection with weekly model evaluation

### 🏗️ Architecture
- **Backend**: FastAPI (Python 3.11+) with async SQLAlchemy
- **Frontend**: React 18 + TypeScript + Vite
- **Database**: PostgreSQL 15 with async connection pooling
- **ML Stack**: XGBoost, Scikit-learn, SHAP, Pandas
- **Deployment**: Docker Compose (production-ready)

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [WooCommerce Integration](#-woocommerce-integration)
- [Model Training](#-model-training)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Monitoring](#-monitoring)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Quick Start

Get the system running in **under 5 minutes**:

```bash
# Clone the repository
git clone https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce.git
cd fraud_detection_system_ecommerce

# Copy environment file
cp .env.example .env

# Start all services with Docker Compose
docker compose up -d

# Wait 30 seconds for services to initialize, then open:
# - Dashboard: http://localhost:3000
# - API Docs: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
```

The system will automatically:
1. ✅ Train an initial fraud detection model on synthetic data
2. ✅ Generate 100 sample transactions with predictions
3. ✅ Start the FastAPI backend on port 8000
4. ✅ Start the React frontend on port 3000

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WooCommerce Store                        │
│                  (PHP Plugin Integration)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ POST /predict
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   FastAPI Backend (Port 8000)               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Prediction │  │   Training   │  │  Dashboard   │      │
│  │   Service   │  │   Service    │  │   Service    │      │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                │                  │               │
│  ┌──────▼────────────────▼──────────────────▼──────┐       │
│  │         XGBoost Model + SHAP Explainer          │       │
│  └──────────────────────┬───────────────────────────┘       │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────┐       │
│  │  PostgreSQL Database (Async SQLAlchemy)         │       │
│  │  - Transactions  - Predictions  - Audit Logs    │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│            React Dashboard (Port 3000)                      │
│  - Fraud Rate Trends  - Model Metrics  - Transaction List  │
│  - SHAP Visualizations  - Real-time Stats                  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Transaction Submission**: WooCommerce sends transaction to `/predict` endpoint
2. **Feature Engineering**: Backend extracts 13 features (amount, merchant, device, time, etc.)
3. **ML Prediction**: XGBoost model predicts fraud probability with SHAP explanations
4. **Database Logging**: Transaction + prediction stored with audit trail
5. **Response**: Returns verdict (fraud/legitimate), confidence, top risk factors
6. **Dashboard**: React UI visualizes fraud trends and individual transaction details

---

## 📦 Installation

### Prerequisites

- **Docker & Docker Compose** (recommended) - [Install Docker](https://docs.docker.com/get-docker/)
- **OR** Manual setup:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce.git
cd fraud_detection_system_ecommerce

# Create .env file
cp .env.example .env

# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/frauddb"
export MODEL_VERSION="v1.0.0"

# Run migrations (if using Alembic)
# alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set API URL
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev

# Build for production
npm run build
```

#### Database

```sql
-- Create database
CREATE DATABASE frauddb;

-- Tables are created automatically on first run
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in the root directory:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://frauduser:fraudpass@db:5432/frauddb
POSTGRES_USER=frauduser
POSTGRES_PASSWORD=fraudpass
POSTGRES_DB=frauddb

# Model Configuration
MODEL_VERSION=v1.0.0
FRAUD_THRESHOLD=0.5
MAX_LATENCY_MS=500

# Security
API_KEY=your-secure-api-key-here  # For /retrain endpoint
RATE_LIMIT_PER_SECOND=100

# Training Parameters
RECALL_THRESHOLD=0.90
PRECISION_THRESHOLD=0.85
FPR_THRESHOLD=0.05

# Data Generation (for demo)
SYNTHETIC_TRANSACTIONS=100
FRAUD_RATE_TARGET=0.15
```

### Model Parameters

Edit `backend/app/ml/config.py`:

```python
XGBOOST_PARAMS = {
    'n_estimators': 200,
    'max_depth': 6,
    'learning_rate': 0.1,
    'scale_pos_weight': 5.0,  # Handles class imbalance
    'eval_metric': 'aucpr',
}

FEATURE_COLUMNS = [
    'amount', 'merchant_id', 'payment_method', 'is_new_user',
    'billing_shipping_match', 'hour_of_day', 'day_of_week',
    'items_count', 'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos',
    'amount_log'
]
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Predict Fraud

**POST** `/predict`

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 299.99,
    "merchant_id": "MCH_12345",
    "payment_method": "credit_card",
    "user_id_hash": "abc123",
    "ip_hash": "192.168.1.1",
    "email_domain": "gmail.com",
    "is_new_user": false,
    "device_type": "mobile",
    "billing_shipping_match": true,
    "hour_of_day": 14,
    "day_of_week": 2,
    "items_count": 3
  }'
```

**Response** (200 OK):
```json
{
  "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
  "label": "legitimate",
  "confidence": 0.92,
  "top_features": [
    {"feature": "amount", "contribution": -0.15},
    {"feature": "is_new_user", "contribution": -0.08},
    {"feature": "hour_sin", "contribution": 0.05}
  ],
  "threshold_used": 0.5,
  "model_version": "v1.0.0",
  "latency_ms": 45.2
}
```

#### 2. Dashboard Summary

**GET** `/dashboard/summary`

```bash
curl http://localhost:8000/api/v1/dashboard/summary
```

**Response**:
```json
{
  "total_predictions": 1247,
  "fraud_count": 187,
  "legitimate_count": 1060,
  "fraud_rate": 0.15,
  "avg_confidence": 0.89,
  "model_version": "v1.0.0",
  "model_recall": 0.94,
  "model_precision": 0.87,
  "model_fpr": 0.04
}
```

#### 3. Transaction Detail

**GET** `/dashboard/transaction/{transaction_id}`

```bash
curl http://localhost:8000/api/v1/dashboard/transaction/550e8400-e29b-41d4-a716-446655440000
```

#### 4. Train Model

**POST** `/retrain`

```bash
curl -X POST http://localhost:8000/api/v1/retrain \
  -H "X-API-Key: your-secure-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "v1.1.0",
    "training_data_path": "data/transactions_labeled.csv"
  }'
```

#### 5. Health Check

**GET** `/health`

```bash
curl http://localhost:8000/health
```

**Interactive Documentation**: http://localhost:8000/docs

---

## 🛒 WooCommerce Integration

### 📦 Download Plugin

**Latest Release:** [v2.2.1](https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/releases/tag/v2.2.1) - **Production Ready**

[![Download Plugin](https://img.shields.io/badge/Download-WooCommerce%20Plugin%20v2.2.1-blue?style=for-the-badge&logo=wordpress)](https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/releases/download/v2.2.1/wc-fraud-detection-v2.2.1-FIXED.zip)
[![Download PDF Manual](https://img.shields.io/badge/Download-PDF%20Manual-red?style=for-the-badge&logo=adobe)](https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/releases/download/v2.2.1/AI_Fraud_Detection_User_Manual_v2.2.1.pdf)

### Quick Installation

1. **Download Plugin**
   - Download [wc-fraud-detection-v2.2.1-FIXED.zip](https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/releases/download/v2.2.1/wc-fraud-detection-v2.2.1-FIXED.zip)

2. **Install in WordPress**
   - Go to WordPress Admin → Plugins → Add New → Upload Plugin
   - Choose the downloaded ZIP file
   - Click "Install Now" then "Activate Plugin"

3. **Configure Settings**
   - Navigate to WooCommerce → Fraud Detection
   - Set API Endpoint: `http://localhost:8000` (or your cloud URL)
   - Set Fraud Threshold: `0.7` (70% confidence - recommended)
   - Enable "Automatic Detection" ✓
   - Enable "Auto-Hold Suspicious Orders" ✓
   - Enable "Email Alerts" ✓
   - Click "Test Connection" to verify
   - Save changes

### Features

#### Core Features
- ✅ **Real-time fraud detection** - Automatic checking on all new orders (<200ms)
- ✅ **Manual fraud check** - On-demand verification with one-click button
- ✅ **CSV bulk upload** - Check hundreds of transactions at once
- ✅ **Auto-hold suspicious orders** - Automatically set to "On Hold" status
- ✅ **Email notifications** - Instant alerts when fraud is detected
- ✅ **Explainable AI** - See top 3 contributing factors for each decision
- ✅ **Real-time progress** - Track CSV processing with progress bars
- ✅ **Results export** - Download fraud reports as CSV
- ✅ **Configurable threshold** - Adjust sensitivity (0.0 - 1.0)

#### New in v2.2.1
- 🆕 **CSV Bulk Upload** - Process historical transactions in batches
- 🆕 **Manual Check Button** - Check any order on-demand
- 🆕 **Progress Tracking** - Real-time progress bars for bulk operations
- 🆕 **Results Dashboard** - Summary statistics and detailed tables
- 🐛 **Fixed CSV Parsing** - Better handling of line endings

### Documentation

- **Quick Start:** [woocommerce-plugin/00-START-HERE.md](woocommerce-plugin/00-START-HERE.md)
- **User Manual:** [woocommerce-plugin/USER_MANUAL.md](woocommerce-plugin/USER_MANUAL.md)
- **PDF Manual:** [Download](https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/releases/download/v2.2.1/AI_Fraud_Detection_User_Manual_v2.2.1.pdf)
- **Installation Guide:** [woocommerce-plugin/INSTALL.md](woocommerce-plugin/INSTALL.md)
- **Release Notes:** [woocommerce-plugin/RELEASE_NOTES_v2.2.1.md](woocommerce-plugin/RELEASE_NOTES_v2.2.1.md)
- **Publishing Guide:** [woocommerce-plugin/PUBLISHING_GUIDE.md](woocommerce-plugin/PUBLISHING_GUIDE.md)

### How It Works

```php
// Plugin intercepts checkout process
add_action('woocommerce_checkout_order_processed', 'fraud_detection_check_order', 10, 1);

function fraud_detection_check_order($order_id) {
    $order = wc_get_order($order_id);

    // Call ML API
    $response = wp_remote_post($api_url . '/predict', [
        'body' => json_encode([
            'amount' => $order->get_total(),
            'merchant_id' => get_option('woocommerce_store_id'),
            'payment_method' => $order->get_payment_method(),
            // ... other features
        ])
    ]);

    $result = json_decode($response['body']);

    if ($result->label === 'fraud') {
        // Hold order for manual review
        $order->update_status('on-hold', 'Flagged by AI fraud detection');

        // Send notification to admin
        wp_mail($admin_email, 'Fraud Alert', "Order #$order_id flagged");
    }
}
```

### Configuration Options

- **API URL**: Backend prediction endpoint
- **Fraud Threshold**: Confidence level to flag transactions (0.0-1.0)
- **Action on Fraud**:
  - Hold for Review (recommended)
  - Cancel Order
  - Email Admin Only
- **Whitelist Rules**: Skip fraud check for trusted customers/IPs

---

## 🎓 Model Training

### Quick Train

```bash
# Using make command
make retrain

# Or directly with API
curl -X POST http://localhost:8000/api/v1/retrain \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json"
```

### Training with Custom Data

1. **Prepare CSV File** (required columns):

```csv
transaction_id,amount,merchant_id,payment_method,is_new_user,device_type,billing_shipping_match,hour_of_day,day_of_week,items_count,label
txn_001,299.99,MCH_001,credit_card,false,desktop,true,14,2,3,legitimate
txn_002,1299.00,MCH_002,paypal,true,mobile,false,3,6,1,fraud
```

2. **Upload and Train**:

```python
# Via Python script
import requests

with open('labeled_transactions.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/retrain',
        headers={'X-API-Key': 'your-api-key'},
        json={'version': 'v1.2.0', 'data_path': 'labeled_transactions.csv'}
    )

print(response.json())
# {
#   "version": "v1.2.0",
#   "recall": 0.93,
#   "precision": 0.88,
#   "f1_score": 0.90,
#   "dataset_rows": 5000
# }
```

### Model Metrics & Gates

Training succeeds only if:
- ✅ Recall ≥ 0.90 (catches 90%+ of fraud)
- ✅ Precision ≥ 0.85 (85%+ of flagged transactions are actually fraud)
- ✅ False Positive Rate ≤ 0.05 (only 5% of legitimate transactions flagged)

Models are versioned and stored in `backend/models/`:
```
models/
├── v1.0.0_model.pkl
├── v1.0.0_explainer.pkl
├── v1.1.0_model.pkl
└── active -> v1.1.0_model.pkl  # symlink to active model
```

---

## 🧪 Testing

### Automated Test Suite

```bash
# Run all tests
./test_system.sh

# Or use make
make test
```

**Tests Covered** (10/10 passing):
1. ✅ Service health checks
2. ✅ Model training and versioning
3. ✅ Fraud prediction accuracy
4. ✅ Legitimate transaction detection
5. ✅ SHAP explanations
6. ✅ Response time (p95 < 200ms)
7. ✅ Dashboard summary API
8. ✅ Transaction detail retrieval
9. ✅ Database persistence
10. ✅ Error handling

### Manual Testing

```bash
# Test legitimate transaction
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 49.99,
    "merchant_id": "MCH_SAFE",
    "is_new_user": false,
    "billing_shipping_match": true,
    "hour_of_day": 14,
    "day_of_week": 2
  }'

# Test fraudulent transaction
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2999.00,
    "merchant_id": "MCH_RISKY",
    "is_new_user": true,
    "billing_shipping_match": false,
    "hour_of_day": 3,
    "day_of_week": 6
  }'
```

### Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test 1000 requests with 10 concurrent connections
ab -n 1000 -c 10 -p transaction.json -T application/json \
  http://localhost:8000/api/v1/predict
```

---

## 🚢 Deployment

### Production Deployment (Railway.app)

1. **Install Railway CLI**

```bash
npm install -g @railway/cli
railway login
```

2. **Initialize Project**

```bash
railway init
railway link
```

3. **Add PostgreSQL**

```bash
railway add postgresql
```

4. **Set Environment Variables**

```bash
railway variables set MODEL_VERSION=v1.0.0
railway variables set FRAUD_THRESHOLD=0.5
# Copy other vars from .env.example
```

5. **Deploy**

```bash
railway up
```

Your API will be live at: `https://your-project.railway.app`

### Alternative: Render.com

1. Create `render.yaml`:

```yaml
services:
  - type: web
    name: fraud-detection-backend
    env: docker
    dockerfilePath: ./backend/Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: frauddb
          property: connectionString

  - type: web
    name: fraud-detection-frontend
    env: docker
    dockerfilePath: ./frontend/Dockerfile
    envVars:
      - key: VITE_API_URL
        value: https://fraud-detection-backend.onrender.com

databases:
  - name: frauddb
    databaseName: frauddb
    user: frauduser
```

2. Connect GitHub repository and deploy automatically on push

### Docker Production Build

```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Deploy with optimizations
docker compose -f docker-compose.prod.yml up -d
```

---

## 📊 Monitoring

### Application Metrics

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Monitor database
docker compose exec db psql -U frauduser -d frauddb -c "SELECT COUNT(*) FROM predictions;"
```

### Key Metrics to Track

- **Prediction Latency** (p50, p95, p99)
- **Fraud Rate Trend** (daily/weekly)
- **Model Accuracy** (recall, precision, F1)
- **False Positive Rate**
- **API Uptime**
- **Database Connection Pool**

### Alerts

Set up alerts for:
- 🚨 Model recall drops below 0.85
- 🚨 False positive rate exceeds 0.07
- 🚨 Prediction latency > 500ms
- 🚨 API error rate > 1%

---

## 🎯 Use Cases

### 1. E-commerce Fraud Prevention
- Real-time checkout validation
- Reduce chargebacks by 60-80%
- Protect revenue from fraudulent transactions

### 2. Payment Gateway Integration
- Pre-authorization fraud screening
- Risk scoring for transaction routing
- Adaptive authentication triggers

### 3. Compliance & Audit
- Complete audit trail for PCI-DSS
- GDPR-compliant data handling
- Explainable AI for regulatory requirements

### 4. Business Intelligence
- Fraud pattern analysis
- Merchant risk profiling
- Customer behavior insights

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `./test_system.sh`
5. **Commit**: `git commit -m 'Add amazing feature'`
6. **Push**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style

- **Python**: Follow PEP 8, use `black` for formatting
- **TypeScript**: Use ESLint + Prettier
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **XGBoost** - High-performance gradient boosting
- **SHAP** - Model interpretability
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **WooCommerce** - E-commerce platform

---

## 📧 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/issues)
- **Email**: tanveer.ahmed986@example.com
- **LinkedIn**: [Tanveer Ahmed](https://linkedin.com/in/tanveer-ahmed986)

---

## 🎓 Portfolio Project

This is a **production-grade portfolio project** demonstrating:
- ✅ Full-stack development (FastAPI + React + PostgreSQL)
- ✅ Machine learning engineering (XGBoost + SHAP)
- ✅ Docker containerization
- ✅ RESTful API design
- ✅ Real-time data processing
- ✅ Explainable AI
- ✅ WooCommerce plugin development
- ✅ Professional documentation

**Perfect for showcasing**: ML engineering, full-stack skills, and production deployment experience.

---

<div align="center">

**Built with ❤️ using FastAPI, React, and XGBoost**

[⭐ Star this repo](https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce) • [🐛 Report Bug](https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/issues) • [✨ Request Feature](https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/issues)

</div>
