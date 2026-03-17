# 🏗️ Backend Setup Guide for Merchants

## Understanding the Architecture

The **WooCommerce Fraud Detection Plugin** requires a **backend API** to analyze transactions. Here's what you need to know:

---

## 🎯 What You Need

```
┌──────────────────────────────────────────────────────────────┐
│  YOUR WORDPRESS SITE (WooCommerce)                           │
│  ├── WooCommerce Plugin Installed ✅                         │
│  └── Configured with API Endpoint                            │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ Sends transaction data
                            │ via HTTPS
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  FRAUD DETECTION API (Required)                              │
│  ├── FastAPI Backend                                         │
│  ├── ML Model (XGBoost)                                      │
│  └── PostgreSQL Database                                     │
└──────────────────────────────────────────────────────────────┘
```

**Bottom line:** You need a fraud detection API running somewhere. You have 3 options.

---

## ✅ **Option 1: Use Our Hosted Service** (Easiest - Recommended for Most)

### What You Get:
- ✅ **Zero setup** - API already running
- ✅ **Maintained by us** - Updates, security patches, monitoring
- ✅ **Shared infrastructure** - Lower cost
- ✅ **5-minute setup** - Just configure the plugin

### Pricing:
- **FREE Tier**: 100 transactions/month
- **Starter**: $29/month - 1,000 transactions
- **Business**: $99/month - 10,000 transactions
- **Enterprise**: Custom pricing

### Setup Instructions:

**Step 1: Get API Credentials**
```
1. Visit: https://fraud-detection-api.example.com/signup
2. Create account (email + password)
3. Get your API key: xxxx-xxxx-xxxx-xxxx
```

**Step 2: Configure Plugin**
```
1. WordPress Admin → WooCommerce → Fraud Detection
2. Enter API Endpoint: https://fraud-detection-api.example.com
3. Enter API Key: xxxx-xxxx-xxxx-xxxx
4. Click "Test Connection" ✅
5. Save Settings
```

**Step 3: Done!**
```
✅ Automatic fraud detection is now active
✅ Every order is analyzed in real-time
✅ You receive email alerts for fraud
```

### Notes:
- ⚠️ **Shared API** - Your data is isolated but infrastructure is shared
- ⚠️ **Monthly billing** - Subscription-based pricing
- ⚠️ **Internet required** - API is cloud-hosted
- ✅ **No technical knowledge needed** - We handle everything

---

## 🐳 **Option 2: Self-Host (Local Server)** (Full Control)

### What You Get:
- ✅ **Complete control** - You own the infrastructure
- ✅ **No monthly fees** - Only hosting costs
- ✅ **Data privacy** - Everything stays on your servers
- ✅ **Customizable** - Modify the ML model, rules, etc.

### Requirements:
- Linux server (Ubuntu 22.04+ recommended)
- 2 CPU cores, 4GB RAM minimum
- 20GB disk space
- Docker installed
- Public IP or domain name

### Setup Instructions:

**Step 1: Clone Repository**
```bash
# SSH into your server
ssh user@your-server.com

# Clone the fraud detection system
git clone https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce.git
cd fraud_detection_system_ecommerce
```

**Step 2: Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env

# Set these values:
DATABASE_URL=postgresql://user:password@localhost:5432/frauddb
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-woocommerce-site.com
```

**Step 3: Start Services**
```bash
# Start with Docker Compose
docker compose up -d

# Verify services are running
docker compose ps

# Expected output:
# backend     Up      0.0.0.0:8000->8000/tcp
# frontend    Up      0.0.0.0:3000->3000/tcp
# postgres    Up      5432/tcp
```

**Step 4: Train Initial Model**
```bash
# Upload training data
curl -X POST http://localhost:8000/retrain \
  -H "Content-Type: application/json" \
  -d @backend/data/labeled_transactions.json

# Verify model is loaded
curl http://localhost:8000/health
# Should show: model_loaded: true
```

**Step 5: Configure Plugin**
```
1. WordPress Admin → WooCommerce → Fraud Detection
2. Enter API Endpoint: http://your-server.com:8000
   (or https://your-server.com if using SSL)
3. Leave API Key blank (or set one in .env)
4. Click "Test Connection" ✅
5. Save Settings
```

**Step 6: Done!**
```
✅ Self-hosted fraud detection is active
✅ All data stays on your server
✅ Zero monthly API fees
```

### Ongoing Maintenance:
```bash
# Update to latest version
cd fraud_detection_system_ecommerce
git pull
docker compose down
docker compose up -d --build

# View logs
docker compose logs -f backend

# Backup database
docker exec -t postgres pg_dump -U postgres frauddb > backup.sql
```

### Notes:
- ⚠️ **Technical knowledge required** - Linux, Docker, networking
- ⚠️ **You manage updates** - Security patches, bug fixes
- ⚠️ **Server costs** - $10-50/month depending on provider
- ✅ **Complete privacy** - No data sent to third parties

---

## ☁️ **Option 3: Cloud Deployment** (Recommended for Scale)

### What You Get:
- ✅ **Scalable** - Handle thousands of transactions
- ✅ **Reliable** - 99.9% uptime guarantees
- ✅ **Managed** - Auto-updates, monitoring, backups
- ✅ **Affordable** - Pay only for what you use

### Platform Options:

#### **3A: Render.com** (Easiest Cloud Deployment)

**Cost:** ~$7/month (starter) to $25/month (standard)

**Setup:**
```bash
1. Create Render account: https://render.com
2. Click "New +" → Web Service
3. Connect GitHub repo: fraud_detection_system_ecommerce
4. Settings:
   - Name: fraud-detection-api
   - Environment: Docker
   - Plan: Starter ($7/mo) or Standard ($25/mo)
5. Add PostgreSQL database:
   - "New +" → PostgreSQL
   - Plan: Starter ($7/mo)
   - Copy DATABASE_URL
6. Set environment variables:
   DATABASE_URL: (from PostgreSQL service)
   SECRET_KEY: (generate random string)
   CORS_ORIGINS: https://your-woocommerce-site.com
7. Deploy
```

**Your API will be:** `https://fraud-detection-api.onrender.com`

#### **3B: Railway.app** (Developer-Friendly)

**Cost:** ~$5/month

**Setup:**
```bash
1. Create Railway account: https://railway.app
2. New Project → Deploy from GitHub
3. Select: fraud_detection_system_ecommerce
4. Add PostgreSQL database (Railway template)
5. Set environment variables (same as Render)
6. Deploy
```

**Your API will be:** `https://fraud-detection-api.up.railway.app`

#### **3C: DigitalOcean App Platform**

**Cost:** ~$12/month

**Setup:**
```bash
1. Create DigitalOcean account
2. Apps → Create App
3. Select GitHub repo
4. Add PostgreSQL database
5. Configure environment
6. Deploy
```

**Your API will be:** `https://fraud-detection-api.ondigitalocean.app`

#### **3D: AWS (EC2 + RDS)** (Enterprise Scale)

**Cost:** ~$50/month (t3.medium + RDS)

**Setup:**
```bash
# Launch EC2 instance (Ubuntu 22.04)
# Install Docker
# Deploy same as Option 2 (self-host)
# Use RDS PostgreSQL database
# Configure Load Balancer + SSL
```

### Configure Plugin:
```
1. WordPress Admin → WooCommerce → Fraud Detection
2. Enter API Endpoint: https://your-cloud-api.com
3. Enter API Key: (if configured)
4. Test Connection ✅
5. Save Settings
```

### Notes:
- ✅ **Best of both worlds** - Managed but isolated
- ✅ **Automatic scaling** - Handle traffic spikes
- ✅ **SSL included** - HTTPS by default
- ⚠️ **Monthly cost** - $5-50/month depending on platform

---

## 📊 **Comparison Table**

| Feature | Hosted Service | Self-Hosted | Cloud Deployment |
|---------|----------------|-------------|------------------|
| **Setup Time** | 5 minutes | 1 hour | 30 minutes |
| **Technical Skill** | None | Advanced | Intermediate |
| **Monthly Cost** | $29-99 | $10-20 (server) | $5-50 (platform) |
| **Data Privacy** | Shared | Full | Full |
| **Maintenance** | None | Manual | Minimal |
| **Scalability** | Limited | Manual | Automatic |
| **Uptime** | 99.9% | Your responsibility | 99.9% |
| **Support** | Included | Self-support | Platform support |

---

## 🎯 **Which Option Should You Choose?**

### Choose **Hosted Service** if:
- ✅ You want zero technical hassle
- ✅ You process <10,000 transactions/month
- ✅ You're okay with monthly subscription
- ✅ You trust third-party infrastructure

### Choose **Self-Hosted** if:
- ✅ You have technical expertise (Linux, Docker)
- ✅ You want complete data control
- ✅ You already have servers
- ✅ You want to customize the ML model

### Choose **Cloud Deployment** if:
- ✅ You want scalability + control
- ✅ You need high uptime guarantees
- ✅ You prefer pay-as-you-go pricing
- ✅ You want managed infrastructure

---

## 🔐 **Security Considerations**

### For ALL Options:
```
✅ HTTPS/SSL Required
   - Use SSL certificate for API endpoint
   - Never use http:// in production

✅ API Key Authentication
   - Set API_KEY in .env
   - Configure in WordPress plugin settings

✅ CORS Configuration
   - Whitelist your WordPress domain only
   - Prevent unauthorized access

✅ Rate Limiting
   - API has built-in rate limiting (100 req/min)
   - Prevents abuse and DDoS

✅ Data Encryption
   - Sensitive data hashed before storage
   - No credit card data transmitted
```

### What the Plugin Sends:
```json
{
  "amount": 99.99,
  "payment_method": "credit_card",
  "email": "customer@example.com",  // Hashed on API side
  "billing_city": "New York",
  "is_new_customer": true,
  "items_count": 2,
  "ip_address": "192.168.1.1"  // Hashed on API side
}
```

**NOT Sent:**
- ❌ Credit card numbers
- ❌ CVV codes
- ❌ Full names
- ❌ Passwords

---

## 🆘 **Troubleshooting**

### Plugin says "Connection Failed"

**Cause:** API is not reachable

**Fix:**
```bash
# Test API manually
curl https://your-api-endpoint.com/health

# Should return:
# {"status": "healthy", "model_loaded": true}

# If timeout, check:
1. API is running: docker compose ps
2. Firewall allows port 8000
3. Domain/IP is correct
4. SSL certificate is valid
```

### "Model not loaded" error

**Cause:** ML model hasn't been trained

**Fix:**
```bash
# Train initial model
curl -X POST http://your-api/retrain \
  -H "Content-Type: application/json" \
  -d @backend/data/labeled_transactions.json
```

### Predictions are slow (>500ms)

**Cause:** Resource constraints

**Fix:**
```bash
# Option 1: Upgrade server resources
# - Add more RAM (4GB → 8GB)
# - Add more CPU (2 cores → 4 cores)

# Option 2: Enable caching
# In .env:
ENABLE_PREDICTION_CACHE=true
CACHE_TTL=300  # 5 minutes

# Option 3: Use cloud auto-scaling
# Deploy to Render/Railway with auto-scaling enabled
```

---

## 📞 **Support**

### Community Support (Free):
- **GitHub Issues:** https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/issues
- **Documentation:** See woocommerce-plugin/USER_MANUAL.md
- **FAQ:** See readme.txt

### Commercial Support (Paid):
- **Email:** tanveer030402@gmail.com
- **Setup Assistance:** $99 one-time (we deploy for you)
- **Custom Integration:** $299+ (tailored to your needs)

---

## 🎊 **Summary**

```
MERCHANT NEEDS:
1. WooCommerce Plugin (FREE - download from GitHub)
2. Backend API (Choose one option above)

SETUP TIME:
- Hosted Service: 5 minutes
- Cloud Deployment: 30 minutes
- Self-Hosted: 1 hour

COSTS:
- Plugin: $0 (FREE forever)
- Backend: $0-99/month (depends on option)

DATA PRIVACY:
- Self-hosted: 100% private
- Cloud: Isolated infrastructure
- Hosted: Shared infrastructure (isolated data)
```

---

## 🚀 **Ready to Deploy?**

### Quick Start Checklist:

**For Hosted Service:**
- [ ] Sign up for hosted service
- [ ] Get API key
- [ ] Configure WordPress plugin
- [ ] Test with sample order
- [ ] Done! ✅

**For Self-Hosted:**
- [ ] Provision Linux server
- [ ] Install Docker
- [ ] Clone repository
- [ ] Configure .env
- [ ] Run docker compose up
- [ ] Train initial model
- [ ] Configure WordPress plugin
- [ ] Test with sample order
- [ ] Done! ✅

**For Cloud Deployment:**
- [ ] Choose platform (Render/Railway/DO)
- [ ] Create account
- [ ] Connect GitHub repo
- [ ] Add PostgreSQL database
- [ ] Set environment variables
- [ ] Deploy
- [ ] Configure WordPress plugin
- [ ] Test with sample order
- [ ] Done! ✅

---

**Questions?** See USER_MANUAL.md or open a GitHub issue!

**Version:** 2.2.1
**Last Updated:** March 17, 2026
