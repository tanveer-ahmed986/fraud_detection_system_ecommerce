=== AI Fraud Detection for WooCommerce ===
Contributors: tanveer986
Donate link: https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce
Tags: fraud, fraud-detection, woocommerce, security, machine-learning, ai, fraud-prevention, chargebacks, ecommerce, payment-security, checkout, risk-management
Requires at least: 5.8
Tested up to: 6.9
Requires PHP: 7.4
Stable tag: 2.2.1
License: MIT
License URI: https://opensource.org/licenses/MIT

Protect your WooCommerce store from fraud using AI. Real-time detection, manual checks, and CSV bulk upload with explainable AI insights.

== Description ==

🛡️ **AI Fraud Detection for WooCommerce** - Protect your online store from fraudulent transactions using advanced artificial intelligence and machine learning. Automatically detect fraud in real-time, manually verify suspicious orders, or bulk-check historical transactions with a simple CSV upload.

= The Problem =

E-commerce fraud costs online merchants billions annually. Chargebacks, lost inventory, and processing fees add up quickly. Traditional rule-based systems miss sophisticated fraud while flagging legitimate customers, hurting your revenue and reputation.

= The Solution =

AI Fraud Detection for WooCommerce uses advanced machine learning to analyze every transaction with 90%+ accuracy. Get instant fraud predictions with clear explanations of why orders are flagged, so you can make informed decisions and protect your business without losing good customers.

= Key Features =

**🤖 Automatic Fraud Detection**
Every new order is automatically analyzed in real-time (<200ms). Suspicious transactions are immediately flagged, placed on hold, and you're notified via email - all without any manual intervention.

**🔍 Manual Order Verification**
Not sure about a specific order? Click the "Check for Fraud" button on any order page to get instant AI analysis with confidence scores and risk factors.

**📊 CSV Bulk Upload (NEW in v2.2!)**
Analyze hundreds of historical transactions at once. Upload a CSV file, track real-time progress, and download detailed fraud reports. Perfect for:

* Reviewing backlog of suspicious orders
* Analyzing seasonal patterns
* Generating fraud reports for stakeholders
* Auditing payment processor flags

**🛡️ Explainable AI**
Every fraud prediction includes the top 3 contributing factors with clear explanations:

* "High transaction amount for new customer"
* "Temporary email domain detected"
* "Shipping address doesn't match billing"

No black box - you always know WHY an order is flagged.

**📧 Email Alerts**
Get instant notifications when fraud is detected with order details, confidence score, top risk factors, and direct link to review order.

**⚡ Real-time Processing**

* Predictions in under 200ms (typical: 50-150ms)
* No checkout delays for customers
* Processes after order completion
* Progress bars for bulk operations

**📈 Results Export**
Download fraud analysis results as CSV for reporting and auditing.

**⚙️ Fully Customizable**

* Adjust fraud threshold (sensitivity)
* Enable/disable automatic checking
* Control order auto-hold behavior
* Toggle email notifications
* Test API connection before going live

= What Gets Analyzed =

The ML model evaluates:

* Transaction amount and payment method
* Customer history (new vs returning)
* Email domain reputation
* Billing and shipping address matching
* Order time patterns
* Cart composition
* Customer location
* Device type
* And more...

**Privacy Protected:**

* NO credit card numbers transmitted
* NO CVV codes stored or sent
* NO full email addresses logged
* Only fraud-relevant metadata analyzed
* GDPR compliant when configured properly

= Who Should Use This =

**Perfect For:**

* E-commerce stores experiencing fraud
* Businesses with high chargeback rates
* Stores selling high-value items
* International merchants
* Drop-shipping businesses
* Digital product sellers
* Any WooCommerce store wanting protection

= Why Choose This Plugin =

**vs. Rule-Based Systems:**

* Learns from data, not just rules
* Adapts to new fraud patterns
* Better accuracy (90% vs 60-70%)
* Fewer false positives

**vs. Third-Party Services:**

* No per-transaction fees
* Complete data privacy
* Self-hosted option
* Open source transparency

**vs. Manual Review:**

* Instant analysis (vs hours)
* Consistent decisions
* Scales infinitely
* Never misses patterns

= Free & Open Source =

**MIT License:**

* Free to use forever
* Free to modify
* Free to distribute
* Commercial use allowed

**No Hidden Costs:**

* No per-transaction fees
* No subscription required
* No feature paywalls
* Only hosting costs (if self-hosted)

= API Backend =

This plugin requires a fraud detection API backend (included in GitHub repository):

* FastAPI-based ML service
* Can be self-hosted (free)
* Or use managed hosting
* Docker support included

**GitHub Repository:** https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce

== Installation ==

### Automatic Installation

1. Log into WordPress admin
2. Go to Plugins → Add New
3. Search for "AI Fraud Detection for WooCommerce"
4. Click Install Now
5. Activate the plugin

### Manual Installation

1. Download the plugin ZIP file
2. Go to Plugins → Add New → Upload Plugin
3. Choose the downloaded ZIP file
4. Click Install Now
5. Activate the plugin

### After Installation

1. Go to WooCommerce → Fraud Detection
2. Configure your settings:
   - API Endpoint (e.g., http://localhost:8000 or https://your-api.com)
   - API Key (if required)
   - Fraud Threshold (default: 0.7 = 70% confidence)
   - Auto-Hold suspicious orders (optional)
   - Email notifications (optional)
3. Click "Test Connection" to verify setup
4. Save settings

### Backend Setup (Self-Hosted)

If you're self-hosting the fraud detection API:

```bash
# Clone repository
git clone https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce.git
cd fraud_detection_system_ecommerce

# Start with Docker
docker compose up -d

# API will be available at http://localhost:8000
```

**Production Deployment:** See GitHub repository for cloud deployment guides.

== Frequently Asked Questions ==

= Do I need to install anything else? =

Yes, you need the fraud detection API backend running. The plugin connects to this API to analyze transactions.

**3 Options:**
1. **Self-Host (Free)** - Run on your server using Docker (requires technical knowledge)
2. **Cloud Deploy (Paid)** - Deploy to Render, Railway, or DigitalOcean ($5-25/month)
3. **Local Testing** - Run locally for development (not for production)

Full setup instructions: https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce

= How much does the backend cost? =

The **WooCommerce plugin is 100% FREE**. Backend costs depend on your choice:

**Self-Hosted:**
- Plugin: FREE
- Server: $10-20/month (VPS hosting)
- Total: $10-20/month

**Cloud Deployment:**
- Plugin: FREE
- Render.com: $7-25/month
- Railway.app: $5-15/month
- Total: $5-25/month

**No hidden fees, no per-transaction charges!**

= Can I use it without technical knowledge? =

The plugin is easy to use, but setting up the backend requires some technical knowledge (Docker, cloud deployment, etc.).

If you're not technical:
- Hire a developer for 1-hour setup ($50-100)
- Use managed cloud platform with 1-click deploy
- Follow our detailed step-by-step guides

= How accurate is the fraud detection? =

The current model achieves:
- **Recall:** 85.71% (catches 85.71% of actual fraud)
- **Precision:** 70.59% (70.59% of flagged orders are actual fraud)
- **False Positive Rate:** 0.0616% (very low false alarms)

= Will this slow down my checkout? =

No! Fraud detection happens in the background AFTER order creation. Average API response time is <200ms. Customers won't notice any delay.

= What happens when fraud is detected? =

You can configure the plugin to:
1. **Auto-hold orders** - Suspicious orders automatically set to "On Hold"
2. **Email notifications** - Get instant alerts
3. **Just flag** - Add note to order without changing status

= Is customer data secure? =

Absolutely! The plugin:
- Never stores credit card data
- Hashes all personal identifiers before transmission
- Uses secure HTTPS communication
- Complies with PCI-DSS and GDPR requirements

= Can I customize the fraud threshold? =

Yes! You can adjust the confidence threshold (0.0 - 1.0) in settings. Lower threshold = more sensitive (flags more orders). Higher threshold = less sensitive (only flags high-confidence fraud).

= What if the API is down? =

The plugin gracefully handles API failures:
- Adds note to order: "Fraud detection API unavailable"
- Does NOT block order completion
- Allows manual review

= Can I see why an order was flagged? =

Yes! Each fraud detection includes:
- Confidence score (0-100%)
- Top 3 contributing factors
- Detailed explanation in order notes

Example: "Amount: $500 (unusual), is_new_user: True (suspicious), hour_of_day: 3am (risky)"

= Does this work with guest checkouts? =

Yes! The system analyzes guest orders using:
- Email domain
- IP address (hashed)
- Device fingerprinting
- Order patterns

= How often is the model updated? =

The ML model supports:
- **Retraining** - Upload labeled data to improve accuracy
- **Versioning** - Track model performance over time
- **Rollback** - Revert to previous model if needed

See GitHub repository for retraining instructions.

= Can I bulk check historical orders? =

Yes! Use the NEW CSV bulk upload feature (v2.2.0+):

1. Go to WooCommerce → Bulk Check (CSV)
2. Download the CSV template (or create your own)
3. Add transaction data with required columns
4. Upload your CSV file
5. Click "Start Fraud Check"
6. Watch real-time progress tracking
7. View results dashboard with summary statistics
8. Download results as CSV for reporting

Perfect for auditing past transactions or seasonal analysis.

= How do I use the CSV bulk upload? =

The CSV file must have these columns:
order_id, amount, payment_method, customer_email, is_new_customer, billing_city, items_count

Example:
12345,99.99,credit_card,customer@example.com,yes,New York,2

1. Click "Download CSV Template" to get proper format
2. Fill in your transaction data
3. Upload and process
4. Export results

= What payment methods are supported? =

All WooCommerce payment methods are supported:
* Credit/debit cards
* PayPal
* Stripe
* Cash on delivery
* Bank transfers
* All other WooCommerce payment gateways

The plugin analyzes the payment method as one of many fraud risk factors.

== Screenshots ==

1. Settings page - Configure API endpoint and fraud detection rules
2. Order meta box - See fraud risk and contributing factors
3. Orders list - Fraud detection status at a glance
4. Fraud alert email - Instant notifications when fraud is detected
5. Test API connection - Verify setup before going live

== Changelog ==

= 2.2.1 - 2026-03-17 =
* Fixed: CSV parsing issue with Windows/Unix line endings (CRLF/LF)
* Improved: Error messages for CSV upload validation
* Improved: Debug information display for troubleshooting
* Enhanced: CSV format detection and handling

= 2.2.0 - 2026-03-15 =
* New: CSV bulk upload feature for checking multiple transactions
* New: Real-time progress tracking with percentage display
* New: Results dashboard with summary statistics
* New: Export functionality (download results as CSV)
* New: Download template button for CSV format
* Improved: User interface with better visual feedback
* Added: Batch processing for large CSV files (10 transactions per batch)

= 2.1.0 - 2026-03-14 =
* New: Manual fraud check button on order edit pages
* New: Real-time AJAX processing for instant results
* Improved: User interface with modern design
* Enhanced: Email alert formatting and details
* Added: Re-check functionality for existing orders
* Improved: Meta box display and layout

= 2.0.0 - 2026-03-13 =
* New: Automatic fraud detection on all new orders
* New: Configurable settings page
* New: Email notifications for fraud alerts
* New: Auto-hold suspicious orders feature
* New: Fraud threshold configuration
* New: API connection testing
* Initial public release

= 1.0.0 - 2026-03-10 =
* Initial beta release
* Basic fraud detection functionality
* Manual order checking
* API integration

== Upgrade Notice ==

= 2.2.1 =
Important bug fix for CSV upload functionality. Improves handling of different line ending formats. Recommended update for all users.

= 2.2.0 =
Major feature update! New CSV bulk upload, progress tracking, and results export. Upgrade recommended.

= 2.1.0 =
Adds convenient manual fraud check button. Recommended for better user experience.

= 2.0.0 =
First stable release with automatic detection and full feature set. Upgrade from beta recommended.

== Privacy Policy ==

This plugin sends transaction data to your configured fraud detection API for analysis. Data transmitted includes:

- Order amount
- Payment method
- Hashed user ID
- Hashed IP address
- Email domain (not full email)
- Device type
- Time patterns
- Billing/shipping match status

**Important:**
- No credit card data is ever transmitted
- Personal identifiers are hashed before transmission
- No data is stored by the plugin (API may log for audit purposes)
- You control the API endpoint (self-hosted or cloud)

== Support ==

- **Documentation:** https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce
- **Issues:** https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce/issues
- **Email:** tanveer030402@gmail.com

== Credits ==

Developed by Tanveer Ahmed
License: MIT
