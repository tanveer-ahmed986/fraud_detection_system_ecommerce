import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getTransaction, TransactionDetail as TransactionDetailType } from '../api/client'
import FeatureContribBar from '../components/FeatureContribBar'

export default function TransactionDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [transaction, setTransaction] = useState<TransactionDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return

    const fetchTransaction = async () => {
      try {
        setLoading(true)
        const response = await getTransaction(id)
        setTransaction(response.data)
        setError(null)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load transaction')
        console.error('Error fetching transaction:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchTransaction()
  }, [id])

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div style={{ fontSize: '18px', color: '#636e72' }}>Loading transaction details...</div>
      </div>
    )
  }

  if (error || !transaction) {
    return (
      <div style={{ padding: '40px' }}>
        <div style={{ background: '#fff3cd', border: '1px solid #ffc107', borderRadius: '8px', padding: '20px' }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#856404' }}>⚠️ Error</h3>
          <p style={{ margin: 0, color: '#856404' }}>{error || 'Transaction not found'}</p>
          <button
            onClick={() => navigate('/')}
            style={{
              marginTop: '16px',
              padding: '8px 16px',
              background: '#ffc107',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  const isFraud = transaction.label === 'fraud'
  const verdictColor = isFraud ? '#e74c3c' : '#27ae60'
  const verdictBg = isFraud ? '#ffebee' : '#e8f5e9'

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <button
          onClick={() => navigate('/')}
          style={{
            background: 'none',
            border: 'none',
            color: '#3498db',
            cursor: 'pointer',
            fontSize: '14px',
            padding: '4px 8px',
            marginBottom: '12px',
          }}
        >
          ← Back to Dashboard
        </button>
        <h2 style={{ margin: '0 0 8px 0' }}>Transaction {transaction.transaction_id.slice(0, 13)}...</h2>
        <p style={{ margin: 0, color: '#636e72', fontSize: '14px' }}>
          {new Date(transaction.created_at).toLocaleString()}
        </p>
      </div>

      {/* Verdict Card */}
      <div
        style={{
          background: verdictBg,
          border: `2px solid ${verdictColor}`,
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '24px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '14px', color: '#636e72', marginBottom: '8px' }}>Verdict</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: verdictColor, textTransform: 'uppercase' }}>
              {isFraud ? '🚨 FRAUD' : '✅ LEGITIMATE'}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '14px', color: '#636e72', marginBottom: '8px' }}>Confidence Score</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: verdictColor }}>
              {(transaction.confidence * 100).toFixed(1)}%
            </div>
          </div>
        </div>
        <div style={{ marginTop: '16px', fontSize: '14px', color: '#636e72' }}>
          Model: {transaction.model_version} • Latency: {transaction.latency_ms.toFixed(2)}ms • Threshold:{' '}
          {(transaction.threshold_used * 100).toFixed(0)}%
        </div>
      </div>

      {/* Transaction Details */}
      <div
        style={{
          background: '#fff',
          borderRadius: '8px',
          padding: '24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          marginBottom: '24px',
        }}
      >
        <h3 style={{ margin: '0 0 20px 0', fontSize: '18px' }}>Transaction Details</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
          <DetailItem label="Amount" value={`$${transaction.amount.toFixed(2)}`} />
          <DetailItem label="Merchant ID" value={transaction.merchant_id} />
          <DetailItem label="Payment Method" value={transaction.payment_method} />
          <DetailItem label="Email Domain" value={transaction.email_domain} />
          <DetailItem label="Device Type" value={transaction.device_type} />
          <DetailItem label="New User" value={transaction.is_new_user ? 'Yes' : 'No'} />
          <DetailItem
            label="Billing/Shipping Match"
            value={transaction.billing_shipping_match ? 'Yes' : 'No'}
          />
          <DetailItem label="Items Count" value={transaction.items_count.toString()} />
          <DetailItem label="Hour of Day" value={`${transaction.hour_of_day}:00`} />
          <DetailItem
            label="Day of Week"
            value={['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][transaction.day_of_week]}
          />
        </div>
      </div>

      {/* Feature Contributions */}
      <div
        style={{
          background: '#fff',
          borderRadius: '8px',
          padding: '24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
      >
        <h3 style={{ margin: '0 0 12px 0', fontSize: '18px' }}>
          🔍 AI Explanation: Top Risk Factors
        </h3>
        <p style={{ margin: '0 0 20px 0', color: '#636e72', fontSize: '14px' }}>
          These features contributed most to the fraud prediction (positive = increases fraud risk, negative = decreases
          risk):
        </p>
        {transaction.top_features.length > 0 ? (
          <>
            <FeatureContribBar features={transaction.top_features} />
            <div style={{ marginTop: '20px', fontSize: '13px', color: '#636e72' }}>
              <strong>How to read this:</strong>
              <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                <li>Red bars (positive) = Feature increases fraud likelihood</li>
                <li>Green bars (negative) = Feature decreases fraud likelihood</li>
                <li>Longer bars = Stronger influence on the prediction</li>
              </ul>
            </div>
          </>
        ) : (
          <div style={{ padding: '20px', background: '#f8f9fa', borderRadius: '4px', textAlign: 'center' }}>
            No feature contributions available
          </div>
        )}
      </div>
    </div>
  )
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div style={{ fontSize: '12px', color: '#95a5a6', marginBottom: '4px', textTransform: 'uppercase' }}>
        {label}
      </div>
      <div style={{ fontSize: '16px', fontWeight: 600, color: '#2c3e50' }}>{value}</div>
    </div>
  )
}
