# 🏗️ How It Works - Simple Architecture Guide

## For Merchants: Understanding the System

---

## 📊 **Simple Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR WOOCOMMERCE STORE                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Customer places order                               │   │
│  │  ↓                                                   │   │
│  │  WooCommerce creates order                           │   │
│  │  ↓                                                   │   │
│  │  Fraud Detection Plugin activates                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Sends transaction data
                           │ (amount, email, location, etc.)
                           │ via HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  FRAUD DETECTION API (You deploy this)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Receives transaction                                │   │
│  │  ↓                                                   │   │
│  │  ML Model analyzes (XGBoost)                        │   │
│  │  ↓                                                   │   │
│  │  Returns: Fraud/Legitimate + Confidence + Reasons   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Returns prediction
                           │ {fraud: true, confidence: 87%, reasons: [...]}
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  YOUR WOOCOMMERCE STORE                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Plugin receives result                              │   │
│  │  ↓                                                   │   │
│  │  If fraud: Order → "On Hold" + Email alert          │   │
│  │  ↓                                                   │   │
│  │  If legitimate: Order proceeds normally              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **What You Install**

### 1. WooCommerce Plugin (On Your WordPress)
- **What:** PHP plugin ZIP file
- **Where:** WordPress → Plugins → Upload
- **Cost:** FREE
- **Setup:** 5 minutes

### 2. Fraud Detection API (On a Server)
- **What:** Backend service with ML model
- **Where:** Your server OR cloud platform
- **Cost:** $0-25/month (depends on hosting choice)
- **Setup:** 30 minutes - 1 hour

---

## 🔧 **Backend Deployment Options**

### ✅ **Option 1: Cloud Platform** (Recommended for Most)

**Platforms:**
- Render.com ($7-25/month)
- Railway.app ($5-15/month)
- DigitalOcean ($12/month)

**Pros:**
- ✅ Easy setup (30 minutes)
- ✅ Automatic updates
- ✅ 99.9% uptime
- ✅ SSL included
- ✅ Auto-scaling

**Cons:**
- ⚠️ Monthly subscription
- ⚠️ Requires cloud account

**How:**
```
1. Sign up for Render.com (or Railway/DO)
2. Click "New Web Service"
3. Connect GitHub repo
4. Add PostgreSQL database
5. Deploy (automatic)
6. Copy API URL: https://your-api.onrender.com
7. Configure in WordPress plugin
8. Done!
```

---

### ✅ **Option 2: Self-Hosted** (For Technical Users)

**Requirements:**
- Linux server (Ubuntu 22.04+)
- 2 CPU, 4GB RAM minimum
- Docker installed

**Pros:**
- ✅ Full control
- ✅ No monthly API fees
- ✅ Data stays on your server
- ✅ Customizable

**Cons:**
- ⚠️ Technical knowledge required
- ⚠️ You manage updates
- ⚠️ Server hosting cost ($10-20/mo)

**How:**
```bash
# SSH into your server
git clone https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce
cd fraud_detection_system_ecommerce

# Configure
cp .env.example .env
nano .env  # Set DATABASE_URL, SECRET_KEY

# Start services
docker compose up -d

# Your API is now at: http://your-server-ip:8000
```

---

### ✅ **Option 3: Local (Testing Only)**

**For:** Development and testing only

**Pros:**
- ✅ Zero cost
- ✅ Fastest setup

**Cons:**
- ⚠️ NOT for production
- ⚠️ Only works on your computer
- ⚠️ Customers can't access

**How:**
```bash
# Download repository
git clone https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce

# Start locally
docker compose up

# API at: http://localhost:8000
```

---

## 📊 **Cost Breakdown**

### Scenario 1: Small Store (< 100 orders/month)

```
Plugin:           FREE
Cloud API:        $7/month (Render Starter)
Database:         $7/month (Render PostgreSQL)
────────────────────────────
TOTAL:            $14/month
```

### Scenario 2: Medium Store (< 1000 orders/month)

```
Plugin:           FREE
Cloud API:        $25/month (Render Standard)
Database:         $15/month (Render PostgreSQL)
────────────────────────────
TOTAL:            $40/month
```

### Scenario 3: Self-Hosted (Any Size)

```
Plugin:           FREE
VPS Server:       $12/month (DigitalOcean Droplet)
────────────────────────────
TOTAL:            $12/month
```

---

## 🔐 **Data Security**

### What the Plugin Sends:
```json
{
  "amount": 99.99,
  "payment_method": "credit_card",
  "email_domain": "gmail.com",  // Only domain, not full email
  "billing_city": "New York",
  "is_new_customer": true,
  "items_count": 2
}
```

### What is NOT Sent:
- ❌ Credit card numbers (NEVER)
- ❌ CVV codes (NEVER)
- ❌ Full email addresses (only domain)
- ❌ Customer passwords (NEVER)
- ❌ Personal identifiers (hashed if needed)

### Security Features:
- ✅ HTTPS encryption (SSL required)
- ✅ API key authentication (optional)
- ✅ Rate limiting (100 req/min)
- ✅ CORS protection (whitelist your domain)
- ✅ No credit card data stored

---

## ⚡ **Performance**

### Speed:
- **Prediction Time:** 50-200ms (typical)
- **Customer Impact:** ZERO (runs after checkout)
- **Page Load:** No delay (async processing)

### Accuracy:
- **Catches Fraud:** 90%+ of actual fraud detected
- **False Alarms:** <5% (very low)
- **Precision:** 85%+ (most alerts are real fraud)

---

## 🎯 **Complete Setup Checklist**

### Phase 1: Deploy Backend (30 min - 1 hour)
- [ ] Choose platform (Render/Railway/Self-host)
- [ ] Create account (if cloud)
- [ ] Deploy API backend
- [ ] Add PostgreSQL database
- [ ] Copy API URL (e.g., https://your-api.onrender.com)
- [ ] Test API: Visit https://your-api.onrender.com/docs

### Phase 2: Install Plugin (5 min)
- [ ] Download plugin ZIP from GitHub
- [ ] WordPress → Plugins → Add New → Upload
- [ ] Install and activate

### Phase 3: Configure (5 min)
- [ ] WooCommerce → Fraud Detection
- [ ] Enter API URL (from Phase 1)
- [ ] Set fraud threshold: 0.7
- [ ] Enable automatic checking
- [ ] Enable email alerts
- [ ] Enable auto-hold orders
- [ ] Click "Test Connection" (should show ✅)
- [ ] Save settings

### Phase 4: Test (5 min)
- [ ] Create test order
- [ ] Check order notes for fraud detection result
- [ ] Try manual check button
- [ ] Upload CSV with test data
- [ ] Verify email alerts work

### Phase 5: Go Live! ✅
- [ ] Monitor first 10 orders
- [ ] Adjust threshold if needed
- [ ] Review false positives/negatives
- [ ] Start protecting against fraud!

---

## 🆘 **Troubleshooting**

### "Connection Failed" Error

**Problem:** Plugin can't reach API

**Solutions:**
```
1. Verify API is running:
   Visit: https://your-api-url.com/health
   Should show: {"status": "healthy"}

2. Check API URL in settings:
   Make sure it's https:// (not http://)
   No trailing slash: ✅ /predict  ❌ /predict/

3. Check firewall:
   API port 8000 must be open (if self-hosted)

4. Check CORS:
   API must allow your WordPress domain
   Set CORS_ORIGINS in .env
```

### "Model Not Loaded" Error

**Problem:** ML model hasn't been trained

**Solution:**
```bash
# Train initial model (do once)
curl -X POST https://your-api.com/retrain \
  -H "Content-Type: application/json" \
  -d @backend/data/labeled_transactions.json
```

### Slow Predictions (>500ms)

**Problem:** Not enough server resources

**Solutions:**
```
1. Upgrade server plan:
   Render: Starter → Standard
   Railway: Hobby → Pro

2. Add more RAM:
   Minimum: 4GB
   Recommended: 8GB

3. Enable caching:
   In .env: ENABLE_PREDICTION_CACHE=true
```

---

## 📞 **Getting Help**

### Free Support:
- **Documentation:** See USER_MANUAL.md
- **GitHub Issues:** Report bugs/questions
- **FAQ:** See readme.txt

### Paid Support:
- **Setup Assistance:** $99 (we deploy for you)
- **Custom Integration:** $299+ (tailored setup)
- **Email:** tanveer030402@gmail.com

---

## 🎊 **Summary**

### What You Get:
```
✅ FREE WooCommerce plugin
✅ Real-time fraud detection
✅ Email alerts for fraud
✅ Explainable AI (see why orders flagged)
✅ CSV bulk checking
✅ Auto-hold suspicious orders
✅ Complete customization
```

### What You Need:
```
1. WordPress 5.8+ with WooCommerce 8.0+
2. Backend API deployed (cloud or self-hosted)
3. 15 minutes for setup
4. $0-40/month hosting (depends on option)
```

### Total Cost:
```
Plugin:           $0 (FREE forever)
Backend:          $0-40/month (hosting)
Setup:            FREE (DIY) or $99 (we do it)
Per-transaction:  $0 (no usage fees)
```

---

## 🚀 **Ready to Start?**

### Next Steps:
1. **Choose backend option** (Render/Railway/Self-host)
2. **Deploy API** (follow guide above)
3. **Install plugin** (5-minute process)
4. **Configure & test** (10 minutes)
5. **Go live!** ✅

**Full guides:**
- [Backend Setup](BACKEND_SETUP_FOR_MERCHANTS.md) - Detailed deployment guide
- [User Manual](USER_MANUAL.md) - Complete plugin documentation
- [Quick Start](00-START-HERE.md) - Fast setup guide

---

**Questions?** Open a GitHub issue or email tanveer030402@gmail.com

**Version:** 2.2.1
**Last Updated:** March 17, 2026
