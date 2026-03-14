interface Props {
  title: string
  value: string | number
  subtitle?: string
  color?: string
}

export default function MetricsCard({ title, value, subtitle, color = '#0984e3' }: Props) {
  return (
    <div style={{
      background: '#fff', borderRadius: '8px', padding: '20px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)', flex: '1', minWidth: '200px'
    }}>
      <div style={{ fontSize: '13px', color: '#636e72', marginBottom: '8px' }}>{title}</div>
      <div style={{ fontSize: '28px', fontWeight: 700, color }}>{value}</div>
      {subtitle && <div style={{ fontSize: '12px', color: '#b2bec3', marginTop: '4px' }}>{subtitle}</div>}
    </div>
  )
}
