# Fraud Detection AI System – Specification (SDD)

## 1. System Overview
**Purpose:** Detect fraudulent e-commerce transactions in real-time using AI.  
**Users:** E-commerce merchants (WooCommerce/Stripe), internal analysts.  
**Goals:**  
- Detect ≥90% of fraud  
- Keep false positives ≤5%  
- Provide auditable logs of all detection decisions  

---

## 2. Data Specifications
**Source:** Transaction CSVs or live transaction APIs  
**Fields:**

| Field Name      | Type      | Description                       | Example          |
|-----------------|-----------|-----------------------------------|----------------|
| user_id         | string    | Unique user identifier             | "UUID-1234"    |
| amount          | float     | Transaction amount in USD          | 125.50         |
| ip              | string    | IPv4 address of the user           | "192.168.0.1"  |
| timestamp       | datetime  | Transaction date-time              | "2026-03-11T12:30:00" |
| payment_method  | string    | Type of payment                    | "credit_card"  |
| is_fraud        | int       | Fraud label (1 = fraud, 0 = legit)| 0              |

**Preprocessing Rules:**  
1. Normalize `amount` using StandardScaler  
2. Encode `ip` as integer by removing dots (`192.168.0.1 → 19216801`)  
3. One-hot encode `payment_method`  
4. Split 80% train / 20% test  

---

## 3. Model Specifications
**Primary Model:** Isolation Forest (unsupervised anomaly detection)  
**Backup Models:** Random Forest or Logistic Regression (supervised)  

**Hyperparameters:**  
- Isolation Forest: n_estimators=100, contamination=0.03, random_state=42  
- Random Forest: n_estimators=100, max_depth=10  

**Training Requirements:**  
- Fit model on training data  
- Save trained model locally as `models/fraud_model.pkl`  
- Allow retraining via `train.py`  

**Prediction Requirements:**  
- Input: transaction dict (amount, ip, payment_method, timestamp)  
- Output: JSON `{ "fraud": 0 | 1, "confidence": float }`  

---

## 4. API Specifications
**Framework:** FastAPI  

**Endpoints:**

| Endpoint      | Method | Input                       | Output                               | Description                  |
|---------------|--------|-----------------------------|-------------------------------------|------------------------------|
| `/predict`    | POST   | Transaction dict (JSON)     | `{"fraud":0, "confidence":0.95}`   | Detects fraud in transaction |
| `/retrain`    | POST   | CSV file path               | `{"status":"success"}`              | Retrain model on new data    |

**Performance Requirements:**  
- Response time <500ms per request for ≤50k transactions  
- Handle simultaneous requests ≥5  

---

## 5. Evaluation Specifications
**Metrics:**  
- Accuracy  
- Precision  
- Recall  
- F1-score  

**Target Thresholds:**  
- Recall ≥ 0.9 (detect ≥90% fraud)  
- False positive rate ≤ 0.05  

**Logging:**  
- Store predictions in `logs/predictions.csv` with timestamp, input features, predicted label, confidence  

---

## 6. Plugin / Integration Specifications
**WooCommerce / Stripe Integration:**  
- POST transaction data to local FastAPI `/predict`  
- Flag order if fraud = 1  
- Optional email alert to merchant  

**Plugin Structure:**  
-fraud_plugin/
-fraud_plugin.php
-README.md

-config.json (API endpoint, thresholds)


**Configurable Parameters:**  
- API endpoint URL  
- Fraud detection threshold (default: 0.03 anomaly score)  
- Email notifications on/off  

---

## 7. System Requirements
**Hardware:** i5 10th gen, 12GB RAM, 512GB SSD  
**Software:** Python 3.11+, VS Code, FastAPI, scikit-learn, pandas, joblib, uvicorn, streamlit (optional)  
**Data Resources:** Free Kaggle datasets or synthetic data generated with Faker  

---

## 8. SDD Compliance Rules
- Every feature must have measurable specs (detection rate, false positives, latency)  
- Logging must be persistent and auditable  
- Preprocessing, training, prediction, and API endpoints must follow exact field names/types  

---

## 9. Deliverables
1. `train.py` – trains model on dataset  
2. `predict.py` / FastAPI `main.py` – serves predictions  
3. `models/fraud_model.pkl` – saved model  
4. `logs/predictions.csv` – audit log  
5. WooCommerce / Stripe plugin (`fraud_plugin/`)  
6. README.md with installation, usage, and retraining instructions  

---

## 10. Timeline & Plan (for Claude Code Planning)
**Day 0–1:** Collect data, setup project structure  
**Day 1–2:** Preprocessing and feature engineering  
**Day 2–4:** Train Isolation Forest and Random Forest models  
**Day 4–6:** Build FastAPI endpoints for prediction and retraining  
**Day 6–8:** Create minimal Streamlit dashboard (optional)  
**Day 8–10:** Develop WooCommerce/Stripe plugin for local API calls  
**Day 10–14:** Test system, tune thresholds, generate audit logs, finalize README  

---

**Note for Claude Code:**  
- Generate **full project code** based on above specs  
- Include scripts for **training, prediction, retraining, logging**  
- Build **FastAPI endpoints** exactly as defined  
- Scaffold **plugin folder with config.json and PHP starter file**  
- Follow preprocessing rules exactly  
- Use **free Python packages only**  
- Ensure outputs meet evaluation targets (≥90% recall, ≤5% false positives)  


