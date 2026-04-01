# Deploy Fraud Detection API to Railway.app

Railway.app is **perfect** for ML/Python applications - no serverless limitations!

## Why Railway?
- ✅ Supports large Python packages (XGBoost, scikit-learn)
- ✅ No cold start delays
- ✅ Simple deployment (Git-based)
- ✅ Better for FastAPI than Vercel
- ✅ Free tier: $5/month credit
- ✅ No complex serverless configuration

---

## Quick Start (5 Minutes)

### Step 1: Install Railway CLI
```bash
npm i -g @railway/cli
```

Or download from: https://docs.railway.app/develop/cli

### Step 2: Login
```bash
railway login
```
This opens your browser - authenticate with GitHub.

### Step 3: Deploy from Backend Directory
```bash
cd backend
railway init
```

**Answer prompts:**
- Create new project? **Yes**
- Project name: **fraud-detection-api**
- Environment: **production**

### Step 4: Link and Deploy
```bash
railway up
```

This will:
1. Upload your code (excluding venv via .railwayignore)
2. Install dependencies from requirements-railway.txt
3. Build and deploy
4. Generate a public URL

### Step 5: Get Your API URL
```bash
railway domain
```

Or check dashboard: https://railway.app/dashboard

Your API will be at: `https://fraud-detection-api-production-XXXX.up.railway.app`

---

## Configuration Files (Already Created)

### ✅ Procfile
Tells Railway how to start the app:
```
web: uvicorn vercel_api:app --host 0.0.0.0 --port $PORT
```

### ✅ requirements-railway.txt
Lightweight dependencies (no database):
```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
scikit-learn>=1.4.0
xgboost>=2.0.0
joblib>=1.3.0
numpy>=1.26.0
python-multipart>=0.0.9
```

### ✅ railway.json / railway.toml
Railway configuration (health checks, restart policy)

### ✅ .railwayignore
Excludes venv, tests, logs from deployment

---

## Verify Deployment

Once deployed, test the API:

```bash
# Health check
curl https://your-app.up.railway.app/api/v1/health

# Test prediction
curl -X POST https://your-app.up.railway.app/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "MERCH123",
    "amount": 250.00,
    "currency": "USD",
    "payment_method": "credit_card",
    "user_id_hash": "abc123",
    "ip_hash": "192.168.1.1",
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
  "label": "legitimate",
  "confidence": 0.12,
  "top_features": [
    {"feature": "Transaction Amount", "contribution": 0.35},
    {"feature": "New Customer", "contribution": 0.28},
    {"feature": "Address Match", "contribution": 0.22}
  ],
  "latency_ms": 45.2
}
```

---

## Update WordPress Plugin

After deployment, update your WordPress site:

1. Go to: **WooCommerce → Settings → Fraud Detection**
2. Update **API Endpoint URL** to:
   ```
   https://fraud-detection-api-production-XXXX.up.railway.app
   ```
3. Save changes
4. Test a transaction!

---

## Railway CLI Commands

```bash
# Check status
railway status

# View logs
railway logs

# Open dashboard
railway open

# Redeploy
railway up

# Set environment variables
railway variables set KEY=value

# Check domain
railway domain

# Delete service
railway down
```

---

## Troubleshooting

### Build fails?
Check logs:
```bash
railway logs --deployment
```

### Model not loading?
Ensure models directory is included:
```bash
ls models/  # Should show .pkl files
```

### Port issues?
Railway automatically sets $PORT. The Procfile uses it:
```
uvicorn vercel_api:app --host 0.0.0.0 --port $PORT
```

### Need to redeploy?
```bash
railway up --detach
```

---

## Cost Estimate

**Free Tier:**
- $5 monthly credit
- ~500 hours of usage
- Perfect for portfolio/demo

**Usage Tier:**
- Pay only for what you use
- ~$0.000463/min (~$20/month for 24/7)

---

## Next Steps

1. Deploy to Railway ✓
2. Update WordPress API endpoint ✓
3. Test transactions ✓
4. Monitor with Railway dashboard ✓

**Railway Dashboard:** https://railway.app/dashboard

---

## Comparison: Railway vs Vercel

| Feature | Railway | Vercel |
|---------|---------|--------|
| ML Support | ✅ Excellent | ❌ Limited |
| Package Size | ✅ Unlimited | ❌ ~100MB |
| Cold Starts | ✅ None | ❌ Yes |
| FastAPI | ✅ Native | ⚠️ Complex |
| Deployment | ✅ Simple | ⚠️ Config-heavy |
| Cost | ✅ $5/month free | ✅ Free tier |

**Verdict:** Railway is the right choice for ML APIs!
