import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts'

interface Feature { feature: string; contribution: number }

export default function FeatureContribBar({ features }: { features: Feature[] }) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={features} layout="vertical" margin={{ right: 80 }}>
        <XAxis type="number" domain={[-0.3, 0.3]} />
        <YAxis
          type="category"
          dataKey="feature"
          width={140}
          tick={{ fontSize: 13, fontWeight: 600 }}
        />
        <Tooltip
          formatter={(value: number) => [`${value > 0 ? '+' : ''}${value.toFixed(4)}`, 'Contribution']}
          contentStyle={{ background: '#fff', border: '1px solid #ddd', borderRadius: '4px' }}
        />
        <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
          {features.map((f, i) => (
            <Cell key={i} fill={f.contribution > 0 ? '#e74c3c' : '#27ae60'} />
          ))}
          <LabelList
            dataKey="contribution"
            position="right"
            formatter={(value: number) => `${value > 0 ? '+' : ''}${value.toFixed(4)}`}
            style={{ fontSize: 13, fontWeight: 'bold' }}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
