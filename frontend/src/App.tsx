import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import TransactionDetail from './pages/TransactionDetail'
import ModelComparison from './pages/ModelComparison'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh' }}>
        <nav style={{
          background: '#2d3436', color: '#fff', padding: '12px 24px',
          display: 'flex', gap: '24px', alignItems: 'center'
        }}>
          <h1 style={{ fontSize: '18px', fontWeight: 700 }}>Fraud Detection</h1>
          <Link to="/" style={{ color: '#dfe6e9' }}>Dashboard</Link>
          <Link to="/models" style={{ color: '#dfe6e9' }}>Models</Link>
        </nav>
        <main style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/transaction/:id" element={<TransactionDetail />} />
            <Route path="/models" element={<ModelComparison />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
