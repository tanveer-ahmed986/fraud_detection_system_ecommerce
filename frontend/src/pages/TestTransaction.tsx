import { useState } from 'react'
import { predictTransaction, PredictRequest, PredictResponse } from '../api/client'
import SingleFeatureBar from '../components/SingleFeatureBar'

export default function TestTransaction() {
  const [formData, setFormData] = useState<PredictRequest>({
    merchant_id: 'merchant_demo',
    amount: 250.00,
    payment_method: 'credit_card',
    user_id_hash: 'user_' + Math.random().toString(36).substring(7),
    ip_hash: 'ip_' + Math.random().toString(36).substring(7),
    email_domain: 'gmail.com',
    is_new_user: false,
    device_type: 'desktop',
    billing_shipping_match: true,
    hour_of_day: new Date().getHours(),
    day_of_week: new Date().getDay(),
    items_count: 2,
  })

  const [result, setResult] = useState<PredictResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await predictTransaction(formData)
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get prediction')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: keyof PredictRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const inputStyle = {
    width: '100%',
    padding: '8px 12px',
    border: '1px solid #dfe6e9',
    borderRadius: '4px',
    fontSize: '14px',
  }

  const labelStyle = {
    display: 'block',
    marginBottom: '6px',
    fontSize: '13px',
    fontWeight: 600,
    color: '#2d3436',
  }

  const fieldStyle = {
    marginBottom: '16px',
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '8px' }}>Test Transaction</h2>
      <p style={{ color: '#636e72', marginBottom: '32px' }}>
        Enter transaction details to test fraud detection in real-time
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
        {/* Form Section */}
        <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', border: '1px solid #dfe6e9' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '20px' }}>Transaction Details</h3>

          <form onSubmit={handleSubmit}>
            <div style={fieldStyle}>
              <label style={labelStyle}>Merchant ID</label>
              <input
                style={inputStyle}
                value={formData.merchant_id}
                onChange={(e) => handleChange('merchant_id', e.target.value)}
                placeholder="merchant_123"
              />
            </div>

            <div style={fieldStyle}>
              <label style={labelStyle}>Amount ($)</label>
              <input
                type="number"
                step="0.01"
                style={inputStyle}
                value={formData.amount}
                onChange={(e) => handleChange('amount', parseFloat(e.target.value))}
              />
            </div>

            <div style={fieldStyle}>
              <label style={labelStyle}>Payment Method</label>
              <select
                style={inputStyle}
                value={formData.payment_method}
                onChange={(e) => handleChange('payment_method', e.target.value)}
              >
                <option value="credit_card">Credit Card</option>
                <option value="debit_card">Debit Card</option>
                <option value="paypal">PayPal</option>
                <option value="crypto">Crypto</option>
              </select>
            </div>

            <div style={fieldStyle}>
              <label style={labelStyle}>Email Domain</label>
              <input
                style={inputStyle}
                value={formData.email_domain}
                onChange={(e) => handleChange('email_domain', e.target.value)}
                placeholder="gmail.com"
              />
            </div>

            <div style={fieldStyle}>
              <label style={labelStyle}>Device Type</label>
              <select
                style={inputStyle}
                value={formData.device_type}
                onChange={(e) => handleChange('device_type', e.target.value)}
              >
                <option value="desktop">Desktop</option>
                <option value="mobile">Mobile</option>
                <option value="tablet">Tablet</option>
              </select>
            </div>

            <div style={fieldStyle}>
              <label style={labelStyle}>Items Count</label>
              <input
                type="number"
                min="1"
                style={inputStyle}
                value={formData.items_count}
                onChange={(e) => handleChange('items_count', parseInt(e.target.value))}
              />
            </div>

            <div style={fieldStyle}>
              <label style={labelStyle}>Hour of Day (0-23)</label>
              <input
                type="number"
                min="0"
                max="23"
                style={inputStyle}
                value={formData.hour_of_day}
                onChange={(e) => handleChange('hour_of_day', parseInt(e.target.value))}
              />
            </div>

            <div style={fieldStyle}>
              <label style={labelStyle}>Day of Week (0=Sun, 6=Sat)</label>
              <input
                type="number"
                min="0"
                max="6"
                style={inputStyle}
                value={formData.day_of_week}
                onChange={(e) => handleChange('day_of_week', parseInt(e.target.value))}
              />
            </div>

            <div style={{ ...fieldStyle, display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={formData.is_new_user}
                onChange={(e) => handleChange('is_new_user', e.target.checked)}
                id="is_new_user"
              />
              <label htmlFor="is_new_user" style={{ fontSize: '14px', cursor: 'pointer' }}>
                New User (First Purchase)
              </label>
            </div>

            <div style={{ ...fieldStyle, display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={formData.billing_shipping_match}
                onChange={(e) => handleChange('billing_shipping_match', e.target.checked)}
                id="billing_shipping_match"
              />
              <label htmlFor="billing_shipping_match" style={{ fontSize: '14px', cursor: 'pointer' }}>
                Billing Matches Shipping
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '12px',
                background: loading ? '#b2bec3' : '#0984e3',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                fontSize: '15px',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                marginTop: '8px',
              }}
            >
              {loading ? 'Analyzing Transaction...' : 'Analyze Risk'}
            </button>
          </form>
        </div>

        {/* Results Section */}
        <div>
          {error && (
            <div style={{
              background: '#ff7675',
              color: '#fff',
              padding: '16px',
              borderRadius: '8px',
              marginBottom: '16px',
            }}>
              <strong>Error:</strong> {error}
            </div>
          )}

          {result && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Risk Assessment Card */}
              <div style={{
                background: result.label === 'HIGH RISK' ? '#ff7675' : '#00b894',
                color: '#fff',
                padding: '24px',
                borderRadius: '8px',
                textAlign: 'center',
              }}>
                <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '4px' }}>
                  Risk Assessment
                </div>
                <div style={{ fontSize: '32px', fontWeight: 700, marginBottom: '8px' }}>
                  {result.label === 'HIGH RISK' ? '⚠️ HIGH RISK' : '✅ LOW RISK'}
                </div>
                <div style={{ fontSize: '16px', opacity: 0.95, marginBottom: '8px' }}>
                  Risk Score: {(result.confidence * 100).toFixed(1)}%
                </div>
                <div style={{
                  fontSize: '14px',
                  opacity: 0.9,
                  borderTop: '1px solid rgba(255,255,255,0.3)',
                  paddingTop: '12px',
                  marginTop: '8px'
                }}>
                  {result.label === 'HIGH RISK'
                    ? 'Suspicious patterns detected - Review recommended'
                    : 'Transaction appears safe to process'
                  }
                </div>
              </div>

              {/* Transaction Info */}
              <div style={{
                background: '#fff',
                padding: '20px',
                borderRadius: '8px',
                border: '1px solid #dfe6e9',
              }}>
                <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px', color: '#636e72' }}>
                  Performance
                </h4>
                <div style={{ fontSize: '13px', color: '#2d3436', lineHeight: 1.8 }}>
                  <div><strong>API Latency:</strong> {result.latency_ms.toFixed(1)}ms</div>
                  <div><strong>Model:</strong> XGBoost v2.0</div>
                  <div><strong>Result:</strong> {result.label.toUpperCase()}</div>
                </div>
              </div>

              {/* Risk Factors Analysis */}
              <div style={{
                background: '#fff',
                padding: '20px',
                borderRadius: '8px',
                border: '1px solid #dfe6e9',
              }}>
                <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '8px', color: '#636e72' }}>
                  Risk Factor Analysis
                </h4>
                <p style={{ fontSize: '13px', color: '#636e72', marginBottom: '16px', lineHeight: 1.5 }}>
                  These factors contributed most to the risk assessment:
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {result.top_features.map((f, i) => (
                    <SingleFeatureBar
                      key={i}
                      feature={f.feature}
                      contribution={f.contribution}
                      rank={i + 1}
                      reason={f.reason}
                    />
                  ))}
                </div>
              </div>

              {/* Recommended Actions */}
              <div style={{
                background: result.label === 'HIGH RISK' ? '#fff3cd' : '#d4edda',
                padding: '16px',
                borderRadius: '8px',
                border: result.label === 'HIGH RISK' ? '1px solid #ffc107' : '1px solid #28a745',
                fontSize: '13px',
                lineHeight: 1.6,
                color: '#212529',
              }}>
                <strong style={{ fontSize: '14px' }}>
                  {result.label === 'HIGH RISK' ? '⚠️ Recommended Action' : '✓ Recommended Action'}
                </strong>
                <div style={{ marginTop: '8px' }}>
                  {result.label === 'HIGH RISK' ? (
                    <>
                      <strong>Hold for Manual Review</strong>
                      <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                        <li>Contact customer to verify identity</li>
                        <li>Confirm billing/shipping address matches</li>
                        <li>Request additional payment verification (CVV, 3D Secure)</li>
                        <li>Check previous order history if available</li>
                      </ul>
                      <div style={{
                        marginTop: '12px',
                        padding: '8px',
                        background: 'rgba(255,193,7,0.1)',
                        borderRadius: '4px',
                        fontSize: '12px'
                      }}>
                        <strong>Note:</strong> High-risk doesn't mean confirmed fraud. Manual review helps reduce false positives while protecting against actual fraud.
                      </div>
                    </>
                  ) : (
                    <>
                      <strong>Safe to Process</strong>
                      <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                        <li>Transaction shows low-risk indicators</li>
                        <li>Standard payment processing recommended</li>
                        <li>Continue with normal fulfillment</li>
                      </ul>
                      <div style={{
                        marginTop: '12px',
                        padding: '8px',
                        background: 'rgba(40,167,69,0.1)',
                        borderRadius: '4px',
                        fontSize: '12px'
                      }}>
                        <strong>Tip:</strong> Continue monitoring for unusual patterns in future transactions from this customer.
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {!result && !error && (
            <div style={{
              background: '#f8f9fa',
              padding: '40px',
              borderRadius: '8px',
              textAlign: 'center',
              color: '#636e72',
              border: '2px dashed #dfe6e9',
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
              <div style={{ fontSize: '15px' }}>
                Fill out the form and click <strong>"Analyze Risk"</strong> to see results
              </div>
              <div style={{ fontSize: '13px', marginTop: '12px', color: '#95a5a6' }}>
                Test real-time fraud detection with explainable AI
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Test Scenarios */}
      <div style={{
        marginTop: '32px',
        background: '#fff',
        padding: '24px',
        borderRadius: '8px',
        border: '1px solid #dfe6e9',
      }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Quick Test Scenarios</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
          <button
            onClick={() => setFormData({
              ...formData,
              amount: 50,
              is_new_user: false,
              billing_shipping_match: true,
              items_count: 1,
              payment_method: 'credit_card',
            })}
            style={{
              padding: '12px',
              background: '#ecf0f1',
              border: '1px solid #bdc3c7',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
            }}
          >
            🟢 Low Risk ($50, Regular)
          </button>
          <button
            onClick={() => setFormData({
              ...formData,
              amount: 999,
              is_new_user: true,
              billing_shipping_match: false,
              items_count: 10,
              payment_method: 'crypto',
            })}
            style={{
              padding: '12px',
              background: '#fff3cd',
              border: '1px solid #ffc107',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
            }}
          >
            🟡 Medium Risk ($999, New)
          </button>
          <button
            onClick={() => setFormData({
              ...formData,
              amount: 50000,
              email_domain: 'tempmail.com',
              is_new_user: true,
              billing_shipping_match: false,
              items_count: 20,
              payment_method: 'credit_card',
              hour_of_day: 3,
            })}
            style={{
              padding: '12px',
              background: '#f8d7da',
              border: '1px solid #dc3545',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
            }}
          >
            🔴 Suspicious ($50K New User)
          </button>
        </div>
      </div>
    </div>
  )
}
