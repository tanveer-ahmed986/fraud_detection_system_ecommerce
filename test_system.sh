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
  echo "Response: $RESPONSE"
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
  echo "Response: $RESPONSE"
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
  echo "Response: $RESPONSE"
  ((FAIL++))
fi

# Test 4: Latency Check
echo -n "Test 4: Latency < 200ms... "
LATENCY=$(echo "$RESPONSE" | grep -o '"latency_ms":[0-9.]*' | cut -d: -f2)
if [ -n "$LATENCY" ]; then
  # Use awk for comparison since bc might not be available
  RESULT=$(awk -v lat="$LATENCY" 'BEGIN { if (lat < 200) print "1"; else print "0" }')
  if [ "$RESULT" = "1" ]; then
    echo "✅ PASS ($LATENCY ms)"
    ((PASS++))
  else
    echo "❌ FAIL ($LATENCY ms)"
    ((FAIL++))
  fi
else
  echo "❌ FAIL (Could not extract latency)"
  ((FAIL++))
fi

# Test 5: SHAP Explainability
echo -n "Test 5: SHAP Explainability... "
if echo "$RESPONSE" | grep -q '"top_features"'; then
  FEATURE_COUNT=$(echo "$RESPONSE" | grep -o '"feature":' | wc -l)
  if [ "$FEATURE_COUNT" -ge 3 ]; then
    echo "✅ PASS ($FEATURE_COUNT features)"
    ((PASS++))
  else
    echo "❌ FAIL (Only $FEATURE_COUNT features)"
    ((FAIL++))
  fi
else
  echo "❌ FAIL (No top_features in response)"
  ((FAIL++))
fi

# Test 6: Dashboard Summary API
echo -n "Test 6: Dashboard Summary... "
RESPONSE=$(curl -s http://localhost:8000/api/v1/dashboard/summary)
if echo "$RESPONSE" | grep -q '"total_predictions"'; then
  echo "✅ PASS"
  ((PASS++))
else
  echo "❌ FAIL"
  echo "Response: $RESPONSE"
  ((FAIL++))
fi

# Test 7: Timeseries API
echo -n "Test 7: Timeseries Data... "
RESPONSE=$(curl -s http://localhost:8000/api/v1/dashboard/timeseries)
if echo "$RESPONSE" | grep -q '"fraud_rate"'; then
  echo "✅ PASS"
  ((PASS++))
else
  echo "❌ FAIL"
  ((FAIL++))
fi

# Test 8: Predictions Saved to Database
echo -n "Test 8: Database Persistence... "
BEFORE=$(curl -s http://localhost:8000/api/v1/dashboard/summary | grep -o '"total_predictions":[0-9]*' | cut -d: -f2)
curl -s -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"merchant_id":"test","amount":100,"payment_method":"credit_card","user_id_hash":"test","ip_hash":"test","email_domain":"test.com","is_new_user":false,"device_type":"desktop","billing_shipping_match":true,"hour_of_day":12,"day_of_week":3,"items_count":2}' > /dev/null
sleep 1
AFTER=$(curl -s http://localhost:8000/api/v1/dashboard/summary | grep -o '"total_predictions":[0-9]*' | cut -d: -f2)
if [ "$AFTER" -gt "$BEFORE" ]; then
  echo "✅ PASS (Before: $BEFORE, After: $AFTER)"
  ((PASS++))
else
  echo "❌ FAIL (Before: $BEFORE, After: $AFTER)"
  ((FAIL++))
fi

# Test 9: Frontend Accessible
echo -n "Test 9: Frontend Accessible... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$STATUS" = "200" ]; then
  echo "✅ PASS"
  ((PASS++))
else
  echo "❌ FAIL (HTTP $STATUS)"
  ((FAIL++))
fi

# Test 10: Model Info API
echo -n "Test 10: Model Information... "
RESPONSE=$(curl -s http://localhost:8000/api/v1/models)
if echo "$RESPONSE" | grep -q '"version"'; then
  echo "✅ PASS"
  ((PASS++))
else
  echo "❌ FAIL"
  ((FAIL++))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
echo ""

if [ $FAIL -eq 0 ]; then
  echo "🎉 All tests passed! System is working properly."
  echo ""
  echo "Next steps:"
  echo "  1. Open dashboard: http://localhost:3000"
  echo "  2. Review TESTING_GUIDE.md for detailed testing scenarios"
  echo "  3. Test WooCommerce plugin integration"
  exit 0
else
  echo "⚠️  Some tests failed. Please check:"
  echo "  - All Docker containers are running: docker compose ps"
  echo "  - Backend logs: docker logs fraud_detection_system-backend-1"
  echo "  - Database logs: docker logs fraud_detection_system-db-1"
  exit 1
fi
