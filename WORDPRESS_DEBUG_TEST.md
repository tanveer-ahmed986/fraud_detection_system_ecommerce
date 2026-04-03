# WordPress Plugin Debug Test

The API works correctly when tested directly. The issue is in how WordPress processes the CSV.

I've added debug logging to see exactly what data WordPress sends to the API.

## Step 1: Reinstall Updated Plugin

**IMPORTANT:** You must reinstall to get the fixes!

1. **WordPress → Plugins**
2. **Find "Tanveer FraudShield for WooCommerce"**
3. **Deactivate** it
4. **Delete** it
5. **Plugins → Add New → Upload Plugin**
6. **Choose file:** `D:\ai_projects\fraud_detection_system\tanveer-fraudshield-for-woocommerce.zip`
7. **Install Now** → **Activate**

---

## Step 2: Verify Settings

1. **WooCommerce → FraudShield**
2. **Check settings:**
   - API Endpoint: `https://fraud-detection-api-production-2c2f.up.railway.app`
   - API Key: `TRIAL_Qaa0NiEHiqYOpCO3Py0oww`
   - Currency: USD
   - Threshold: 0.7
3. **Save Settings**

---

## Step 3: Clear WordPress Cache

If you have any caching plugin:
1. **Clear all cache** (WP Super Cache, W3 Total Cache, etc.)
2. **Clear browser cache** (Ctrl+Shift+Delete)
3. **Hard refresh page** (Ctrl+F5)

---

## Step 4: Test CSV Upload

1. **WooCommerce → Bulk Check (CSV)**
2. **Upload:** `D:\ai_projects\fraud_detection_system\test-transactions.csv`
3. **Click "Start Fraud Check"**
4. **Wait for results**

---

## Step 5: Check Debug Logs

While the CSV is processing, WordPress writes debug logs.

**View logs:**

**Option A: WordPress Debug Log (if enabled)**
```
Location: wp-content/debug.log
```

**Option B: PHP Error Log**
```
Check your hosting control panel for PHP error logs
```

**Option C: Browser Console**
```
1. Press F12 (open DevTools)
2. Go to Console tab
3. Look for messages like "CSV Headers:" and "Parsed X rows"
```

**What to look for in logs:**
```
=== CSV BULK CHECK DEBUG ===
CSV Row: {"merchant_id":"MERCH001","amount":"50.00","currency":"USD",...}
Sending to API: {"merchant_id":"MERCH001","amount":50,"payment_method":"credit_card",...}
```

---

## Expected Results (After Fix):

### Row-by-Row Breakdown:

**Row 1:** $5,000, tempmail.com, new user, mobile, 3am
- **Expected:** HIGH RISK (99.99%)

**Row 2:** $50, gmail.com, existing user, desktop, 2pm
- **Expected:** LOW RISK (0.00%)

**Row 3:** $10,000, guerrillamail.com, new user, mobile, 2am
- **Expected:** HIGH RISK (99.99%)

**Row 4:** $250, yahoo.com, existing user, desktop, 10am
- **Expected:** LOW RISK (0.01%)

**Row 5:** $1,500, 10minutemail.net, new user, mobile, 11pm
- **Expected:** HIGH RISK (99.99%)

**Row 6:** $75, outlook.com, existing user, desktop, 3pm
- **Expected:** LOW RISK (0.00%)

**Row 7:** $8,000, throwaway.email, new user, mobile, 4am
- **Expected:** HIGH RISK (99.99%)

**Row 8:** $120, gmail.com, existing user, desktop, 12pm
- **Expected:** LOW RISK (0.00%)

### Summary:
- **4 High Risk** (rows 1, 3, 5, 7)
- **4 Low Risk** (rows 2, 4, 6, 8)

---

## If Still All High Risk:

Send me the debug log output so I can see exactly what data is being sent!

**Copy logs from:**
1. Browser Console (F12 → Console tab)
2. WordPress debug.log file
3. Or take screenshot of results page

---

## Test: Download New Template

The plugin now has the CORRECT CSV template:

1. **WooCommerce → Bulk Check (CSV)**
2. **Click "Download CSV Template"**
3. **Open the downloaded file**
4. **Verify columns:**
   ```
   merchant_id,amount,currency,payment_method,user_id_hash,ip_hash,email_domain,is_new_user,device_type,billing_shipping_match,hour_of_day,day_of_week,items_count
   ```

Old template had: `order_id,customer_email,is_new_customer` (WRONG)
New template has: `merchant_id,email_domain,is_new_user` (CORRECT)

---

## Why Vercel Shows All Low Risk:

The Vercel frontend might be:
1. Using different test data
2. Sending hardcoded values
3. Not sending all required fields

Focus on getting WordPress working first, then we can check Vercel frontend.

---

## Quick Verification:

**Before you test WordPress, run this to verify API works:**

```bash
cd D:\ai_projects\fraud_detection_system
python debug_api_requests.py
```

**Should show:**
- CSV Row 1: HIGH RISK (99.99%)
- CSV Row 2: LOW RISK (0.00%)

If API test works but WordPress still fails, it's a WordPress issue.

---

**Next:** Reinstall plugin, test CSV, and send me the debug logs!
