import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TimeseriesPoint } from '../api/client'

export default function FraudRateChart({ data }: { data: TimeseriesPoint[] }) {
  return (
    <div style={{ background: '#fff', borderRadius: '8px', padding: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Fraud Rate Over Time</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={[...data].reverse()}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tickFormatter={(v: number) => `${(v * 100).toFixed(1)}%`} />
          <Tooltip formatter={(v: number) => `${(v * 100).toFixed(2)}%`} />
          <Line type="monotone" dataKey="fraud_rate" stroke="#d63031" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
