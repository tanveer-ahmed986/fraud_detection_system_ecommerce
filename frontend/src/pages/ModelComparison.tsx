import { useState, useEffect } from 'react'
import { getModels, ModelInfo } from '../api/client'

export default function ModelComparison() {
  const [models, setModels] = useState<ModelInfo[]>([])

  useEffect(() => {
    getModels().then(r => setModels(r.data)).catch(console.error)
  }, [])

  return (
    <div>
      <h2 style={{ marginBottom: '16px' }}>Model Versions</h2>
      <div style={{ background: '#fff', borderRadius: '8px', padding: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #dfe6e9', textAlign: 'left' }}>
              <th style={{ padding: '8px' }}>Version</th>
              <th style={{ padding: '8px' }}>Status</th>
              <th style={{ padding: '8px' }}>Recall</th>
              <th style={{ padding: '8px' }}>Precision</th>
              <th style={{ padding: '8px' }}>F1</th>
              <th style={{ padding: '8px' }}>FPR</th>
              <th style={{ padding: '8px' }}>Rows</th>
              <th style={{ padding: '8px' }}>Created</th>
            </tr>
          </thead>
          <tbody>
            {models.map(m => (
              <tr key={m.version} style={{ borderBottom: '1px solid #f1f2f6', background: m.is_active ? '#f0fff4' : 'transparent' }}>
                <td style={{ padding: '8px', fontWeight: 600 }}>v{m.version}</td>
                <td style={{ padding: '8px' }}>
                  {m.is_active ? <span style={{ color: '#00b894', fontWeight: 600 }}>Active</span> : 'Inactive'}
                </td>
                <td style={{ padding: '8px' }}>{(m.recall * 100).toFixed(1)}%</td>
                <td style={{ padding: '8px' }}>{(m.precision * 100).toFixed(1)}%</td>
                <td style={{ padding: '8px' }}>{(m.f1_score * 100).toFixed(1)}%</td>
                <td style={{ padding: '8px' }}>{(m.fpr * 100).toFixed(1)}%</td>
                <td style={{ padding: '8px' }}>{m.dataset_rows?.toLocaleString()}</td>
                <td style={{ padding: '8px' }}>{new Date(m.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
