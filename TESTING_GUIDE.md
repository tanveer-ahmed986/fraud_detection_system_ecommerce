# Fraud Detection System - Testing Guide

## Quick Start: 5-Minute Verification

### 1. Check All Services Are Running
```bash
docker compose ps
```
**Expected**: All 3 services (db, backend, frontend) should show status "Up"

### 2. Health Check
```bash
curl http://localhost:8000/api/v1/health
```
**Expected Output**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "1.0"
}
```

### 3. Test Prediction - Legitimate Transaction
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "merchant_001",
    "amount": 49.99,
    "payment_method": "credit_card",
    "user_id_hash": "user123hash",
    "ip_hash": "ip456hash",
    "email_domain": "gmail.com",
    "is_new_user": false,
    "device_type": "desktop",
    "billing_shipping_match": true,
    "hour_of_day": 14,
    "day_of_week": 2,
    "items_count": 3
  }'
```
**Expected**:
- `"label": "legitimate"`
- `"confidence"` close to 0.0 (low fraud probability)
- `"latency_ms"` < 200ms
- `"top_features"` array with 3 items

### 4. Test Prediction - Fraudulent Transaction
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "merchant_999",
    "amount": 9999.99,
    "payment_method": "crypto",
    "user_id_hash": "newhash",
    "ip_hash": "suspiciousip",
    "email_domain": "tempmail.net",
    "is_new_user": true,
    "device_type": "mobile",
    "billing_shipping_match": false,
    "hour_of_day": 3,
    "day_of_week": 6,
    "items_count": 1
  }'
```
**Expected**:
- `"label": "fraud"`
- `"confidence"` > 0.5 (high fraud probability)
- `"latency_ms"` < 200ms

### 5. Check Dashboard (Browser)
Open in your browser:
```
http://localhost:3000
```
**Expected**:
- ✅ Dashboard loads successfully
- ✅ Metrics cards showing total predictions, fraud rate, avg confidence, model version
- ✅ Fraud rate chart displaying over time
- ✅ Recent predictions table with your test transactions
- ✅ Click on a transaction ID to see details

---

## Comprehensive Testing

### A. API Endpoint Testing

#### 1. Dashboard Summary
```bash
curl http://localhost:8000/api/v1/dashboard/summary | python -m json.tool
```
**Verify**:
- `total_predictions` > 0
- `fraud_rate` between 0.0 and 1.0
- `model_recall`, `model_precision`, `model_fpr` are present

#### 2. Timeseries Data
```bash
curl http://localhost:8000/api/v1/dashboard/timeseries | python -m json.tool
```
**Verify**:
- Returns array of daily fraud rates
- Each entry has `date`, `total`, `fraud`, `fraud_rate`

#### 3. Predictions History
```bash
curl http://localhost:8000/api/v1/dashboard/predictions?page=1&page_size=10 | python -m json.tool
```
**Verify**:
- Returns paginated predictions
- Each prediction has `transaction_id`, `amount`, `label`, `confidence`, `top_features`

#### 4. Model Information
```bash
curl http://localhost:8000/api/v1/models | python -m json.tool
```
**Verify**:
- Returns model version info
- Shows metrics: `recall`, `precision`, `f1_score`, `fpr`

### B. Performance Testing

#### Test Latency (100 requests)
```bash
for i in {1..100}; do
  curl -s -X POST http://localhost:8000/api/v1/predict \
    -H "Content-Type: application/json" \
    -d '{
      "merchant_id": "merchant_001",
      "amount": 150.0,
      "payment_method": "credit_card",
      "user_id_hash": "hash'$i'",
      "ip_hash": "iphash'$i'",
      "email_domain": "gmail.com",
      "is_new_user": false,
      "device_type": "desktop",
      "billing_shipping_match": true,
      "hour_of_day": 14,
      "day_of_week": 2,
      "items_count": 2
    }' | grep -o '"latency_ms":[0-9.]*'
done | awk -F: '{sum+=$2; count++} END {print "Average latency:", sum/count, "ms"}'
```
**Expected**: Average latency < 200ms

### C. Database Verification

#### Check Predictions Are Saved
```bash
curl "http://localhost:8000/api/v1/dashboard/predictions?page_size=5" | python -m json.tool
```
**Verify**: Recent predictions appear immediately after making them

#### Check Audit Logs
```bash
curl "http://localhost:8000/api/v1/audit/recent?limit=5" 2>/dev/null || echo "Endpoint not exposed (internal only)"
```

### D. Frontend Testing Checklist

Open http://localhost:3000 and verify:

- [ ] **Dashboard Page Loads**
  - No console errors (F12 → Console)
  - All components render correctly

- [ ] **Metrics Cards Display**
  - Total Predictions count
  - Fraud Rate percentage
  - Average Confidence percentage
  - Model version and recall

- [ ] **Fraud Rate Chart**
  - Line chart renders
  - Shows fraud rate over time
  - Axes labeled correctly
  - Tooltip shows values on hover

- [ ] **Predictions Table**
  - Recent predictions listed
  - Transaction IDs are clickable links
  - Amount displayed with $ symbol
  - Verdict shows color-coded badge (fraud = red/yellow, legitimate = gray)
  - Confidence shows as percentage
  - Timestamp formatted correctly

- [ ] **Transaction Detail View**
  - Click a transaction ID
  - Should navigate to `/transaction/{id}` page
  - Shows full transaction details and feature contributions

### E. Edge Cases & Error Handling

#### 1. Invalid Input (Missing Required Fields)
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"amount": 100}'
```
**Expected**: 422 Unprocessable Entity with field validation errors

#### 2. Invalid Data Types
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "merchant_001",
    "amount": "not_a_number",
    "payment_method": "credit_card",
    "user_id_hash": "hash",
    "ip_hash": "iphash",
    "email_domain": "gmail.com",
    "is_new_user": false,
    "device_type": "desktop",
    "billing_shipping_match": true,
    "hour_of_day": 14,
    "day_of_week": 2,
    "items_count": 2
  }'
```
**Expected**: 422 with validation error for `amount` field

#### 3. Boundary Values
```bash
# Test minimum amount
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "merchant_001",
    "amount": 0.01,
    "payment_method": "credit_card",
    "user_id_hash": "hash",
    "ip_hash": "iphash",
    "email_domain": "gmail.com",
    "is_new_user": false,
    "device_type": "desktop",
    "billing_shipping_match": true,
    "hour_of_day": 0,
    "day_of_week": 0,
    "items_count": 1
  }'
```
**Expected**: Valid prediction returned

#### 4. Maximum Hour/Day Values
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "merchant_001",
    "amount": 100,
    "payment_method": "credit_card",
    "user_id_hash": "hash",
    "ip_hash": "iphash",
    "email_domain": "gmail.com",
    "is_new_user": false,
    "device_type": "desktop",
    "billing_shipping_match": true,
    "hour_of_day": 23,
    "day_of_week": 6,
    "items_count": 1
  }'
```
**Expected**: Valid prediction returned

### F. Model Explainability Testing

Check that SHAP explanations are meaningful:
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "merchant_001",
    "amount": 5000,
    "payment_method": "crypto",
    "user_id_hash": "hash",
    "ip_hash": "iphash",
    "email_domain": "tempmail.org",
    "is_new_user": true,
    "device_type": "mobile",
    "billing_shipping_match": false,
    "hour_of_day": 3,
    "day_of_week": 6,
    "items_count": 1
  }' | python -m json.tool
```
**Verify top_features**:
- Contains exactly 3 features
- Each has `feature` name and `contribution` value
- Contributions are non-zero numbers

---

## Automated Test Suite

### Create Test Script
Save as `test_system.sh`:

```bash
#!/bin/bash

echo "=== Fraud Detection System Test Suite ==="
PASS=0
FAIL=0

# Test 1: Health Check
echo -n "Test 1: Health Check... "
RESPONSE=$(curl -s http://localhost:8000/api/v1/health)
if echo "$RESPONSE" | grep -q '"status":"healthy"'; then
  echo "✅ PASS"
  ((PASS++))
else
  echo "❌ FAIL"
  ((FAIL++))
fi

# Test 2: Legitimate Prediction
echo -n "Test 2: Legitimate Transaction... "
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"merchant_id":"m1","amount":50,"payment_method":"credit_card","user_id_hash":"u1","ip_hash":"i1","email_domain":"gmail.com","is_new_user":false,"device_type":"desktop","billing_shipping_match":true,"hour_of_day":14,"day_of_week":2,"items_count":3}')
if echo "$RESPONSE" | grep -q '"label":"legitimate"'; then
  echo "✅ PASS"
  ((PASS++))
else
  echo "❌ FAIL"
  ((FAIL++))
fi

# Test 3: Fraudulent Prediction
echo -n "Test 3: Fraudulent Transaction... "
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"merchant_id":"m999","amount":9999,"payment_method":"crypto","user_id_hash":"new","ip_hash":"sus","email_domain":"tempmail.net","is_new_user":true,"device_type":"mobile","billing_shipping_match":false,"hour_of_day":3,"day_of_week":6,"items_count":1}')
if echo "$RESPONSE" | grep -q '"label":"fraud"'; then
  echo "✅ PASS"
  ((PASS++))
else
  echo "❌ FAIL"
  ((FAIL++))
fi

# Test 4: Latency Check
echo -n "Test 4: Latency < 200ms... "
LATENCY=$(echo "$RESPONSE" | grep -o '"latency_ms":[0-9.]*' | cut -d: -f2)
if (( $(echo "$LATENCY < 200" | bc -l) )); then
  echo "✅ PASS ($LATENCY ms)"
  ((PASS++))
else
  echo "❌ FAIL ($LATENCY ms)"
  ((FAIL++))
fi

# Test 5: Dashboard API
echo -n "Test 5: Dashboard Summary... "
RESPONSE=$(curl -s http://localhost:8000/api/v1/dashboard/summary)
if echo "$RESPONSE" | grep -q '"total_predictions"'; then
  echo "✅ PASS"
  ((PASS++))
else
  echo "❌ FAIL"
  ((FAIL++))
fi

# Test 6: Frontend
echo -n "Test 6: Frontend Accessible... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$STATUS" = "200" ]; then
  echo "✅ PASS"
  ((PASS++))
else
  echo "❌ FAIL (HTTP $STATUS)"
  ((FAIL++))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ $FAIL -eq 0 ]; then
  echo "🎉 All tests passed!"
  exit 0
else
  echo "⚠️  Some tests failed"
  exit 1
fi
```

### Run Automated Tests
```bash
chmod +x test_system.sh
./test_system.sh
```

---

## WooCommerce Plugin Testing

### 1. Install Plugin
```bash
cd plugin
zip -r fraud-detection-plugin.zip fraud-detection-plugin/
```
Upload to WordPress: **Plugins → Add New → Upload Plugin**

### 2. Configure Plugin
- Navigate to **WooCommerce → Fraud Detection**
- Set API URL: `http://your-server:8000`
- Set API Key: `demo-api-key` (from .env)
- Enable fraud detection

### 3. Test Checkout
1. Add product to cart
2. Proceed to checkout
3. Fill in details:
   - **Legitimate test**: Normal email, matching address
   - **Fraud test**: tempmail.org email, mismatched billing/shipping
4. Complete order

**Verify**:
- Order notes show fraud detection result
- Admin receives email notification for fraud
- Transaction appears in dashboard predictions

---

## Performance Benchmarks

### Expected Performance:
- **Latency**: p50 < 100ms, p95 < 200ms, p99 < 500ms
- **Throughput**: > 100 requests/second (single container)
- **Model Size**: ~6 MB (v1.0.joblib)
- **Memory Usage**: Backend ~200MB, Frontend ~50MB
- **Database**: PostgreSQL ~100MB with 10k predictions

### Load Testing (Optional)
Using Apache Bench:
```bash
ab -n 1000 -c 10 -p payload.json -T application/json \
  http://localhost:8000/api/v1/predict
```

---

## Troubleshooting

### Issue: "Model not loaded"
**Solution**:
```bash
docker exec fraud_detection_system-backend-1 ls -l /app/models/
# Should show v1.0.joblib
```

### Issue: Database connection errors
**Solution**:
```bash
docker logs fraud_detection_system-db-1
docker exec fraud_detection_system-db-1 pg_isready -U fraud_user
```

### Issue: Frontend can't reach backend
**Solution**: Check nginx proxy configuration
```bash
docker exec fraud_detection_system-frontend-1 cat /etc/nginx/conf.d/default.conf
```

### Issue: Predictions not saving
**Solution**: Check backend logs for database errors
```bash
docker logs fraud_detection_system-backend-1 --tail 50
```

---

## Success Criteria

✅ **System is working properly if**:

1. All health checks pass
2. Legitimate transactions get confidence < 0.5
3. Fraudulent transactions get confidence > 0.5
4. Latency consistently < 200ms
5. Predictions saved to database immediately
6. Dashboard displays real-time data
7. Frontend accessible and functional
8. Model explainability (top_features) provided
9. No errors in container logs
10. WooCommerce plugin integrates successfully

---

## Daily Monitoring Checklist

- [ ] Check service health: `docker compose ps`
- [ ] Verify model loaded: `curl http://localhost:8000/api/v1/health`
- [ ] Review recent predictions: Check dashboard at http://localhost:3000
- [ ] Check fraud rate trends: Should be stable around 5% for synthetic data
- [ ] Monitor latency: All predictions < 200ms
- [ ] Check logs for errors: `docker logs fraud_detection_system-backend-1 --tail 100`

---

**For Portfolio Reviewers**: Run the automated test script (`test_system.sh`) to verify all core functionality in under 30 seconds.
