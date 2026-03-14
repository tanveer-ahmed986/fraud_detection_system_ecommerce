import { useState, useEffect } from 'react'
import { getSummary, getTimeseries, getPredictions, DashboardSummary, TimeseriesPoint, PredictionItem } from '../api/client'
import MetricsCard from '../components/MetricsCard'
import FraudRateChart from '../components/FraudRateChart'
import PredictionTable from '../components/PredictionTable'

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [timeseries, setTimeseries] = useState<TimeseriesPoint[]>([])
  const [predictions, setPredictions] = useState<PredictionItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getSummary(), getTimeseries(), getPredictions()])
      .then(([s, t, p]) => {
        setSummary(s.data)
        setTimeseries(t.data)
        setPredictions(p.data.predictions)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ padding: '40px', textAlign: 'center' }}>Loading...</div>
  if (!summary) return <div style={{ padding: '40px', textAlign: 'center' }}>Failed to load data</div>

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
        <MetricsCard title="Total Predictions" value={summary.total_predictions.toLocaleString()} />
        <MetricsCard title="Fraud Rate" value={`${(summary.fraud_rate * 100).toFixed(1)}%`} color="#d63031" />
        <MetricsCard title="Avg Confidence" value={`${(summary.avg_confidence * 100).toFixed(1)}%`} />
        <MetricsCard title="Model" value={`v${summary.model_version}`}
          subtitle={summary.model_recall ? `Recall: ${(summary.model_recall * 100).toFixed(0)}%` : undefined} />
      </div>
      <FraudRateChart data={timeseries} />
      <PredictionTable predictions={predictions} />
    </div>
  )
}
