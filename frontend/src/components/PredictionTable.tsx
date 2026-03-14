import { Link } from 'react-router-dom'
import { PredictionItem } from '../api/client'

export default function PredictionTable({ predictions }: { predictions: PredictionItem[] }) {
  return (
    <div style={{ background: '#fff', borderRadius: '8px', padding: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflowX: 'auto' }}>
      <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Recent Predictions</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #dfe6e9', textAlign: 'left' }}>
            <th style={{ padding: '8px' }}>Transaction</th>
            <th style={{ padding: '8px' }}>Amount</th>
            <th style={{ padding: '8px' }}>Verdict</th>
            <th style={{ padding: '8px' }}>Confidence</th>
            <th style={{ padding: '8px' }}>Merchant</th>
            <th style={{ padding: '8px' }}>Time</th>
          </tr>
        </thead>
        <tbody>
          {predictions.map((p) => (
            <tr key={p.transaction_id} style={{ borderBottom: '1px solid #f1f2f6' }}>
              <td style={{ padding: '8px' }}>
                <Link to={`/transaction/${p.transaction_id}`}>{p.transaction_id.slice(0, 8)}...</Link>
              </td>
              <td style={{ padding: '8px' }}>${p.amount.toFixed(2)}</td>
              <td style={{ padding: '8px' }}>
                <span style={{
                  padding: '2px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: 600,
                  background: p.label === 'fraud' ? '#ffeaa7' : '#dfe6e9',
                  color: p.label === 'fraud' ? '#d63031' : '#2d3436',
                }}>{p.label}</span>
              </td>
              <td style={{ padding: '8px' }}>{(p.confidence * 100).toFixed(1)}%</td>
              <td style={{ padding: '8px' }}>{p.merchant_id}</td>
              <td style={{ padding: '8px' }}>{new Date(p.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
