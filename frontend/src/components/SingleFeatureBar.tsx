interface Props {
  feature: string
  contribution: number
  rank: number
  reason?: string  // Human-readable explanation
}

export default function SingleFeatureBar({ feature, contribution, rank, reason }: Props) {
  const maxWidth = 100
  const percentage = Math.min(Math.abs(contribution) * 100, maxWidth)
  const isPositive = contribution > 0

  return (
    <div style={{ marginBottom: '12px' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        marginBottom: '6px',
        fontSize: '13px',
      }}>
        <span style={{ fontWeight: 600, color: '#2d3436' }}>
          #{rank} {feature.replace(/_/g, ' ').toUpperCase()}
        </span>
        <span style={{
          fontWeight: 700,
          color: isPositive ? '#e74c3c' : '#27ae60',
        }}>
          {isPositive ? '+' : ''}{contribution.toFixed(4)}
        </span>
      </div>
      <div style={{
        height: '24px',
        background: '#f0f0f0',
        borderRadius: '4px',
        overflow: 'hidden',
        position: 'relative',
      }}>
        <div style={{
          height: '100%',
          width: `${percentage}%`,
          background: isPositive ? '#e74c3c' : '#27ae60',
          transition: 'width 0.3s ease',
          borderRadius: '4px',
        }} />
      </div>
      <div style={{ fontSize: '12px', color: '#2d3436', marginTop: '6px', fontWeight: 500 }}>
        {reason || (isPositive ? 'Increases fraud risk' : 'Decreases fraud risk')}
      </div>
    </div>
  )
}
