import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import TransactionDetail from './pages/TransactionDetail'
import ModelComparison from './pages/ModelComparison'
import TestTransaction from './pages/TestTransaction'
import BulkCheck from './pages/BulkCheck'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', background: '#f5f6fa' }}>
        <nav style={{
          background: '#2d3436', color: '#fff', padding: '12px 24px',
          display: 'flex', gap: '24px', alignItems: 'center'
        }}>
          <h1 style={{ fontSize: '18px', fontWeight: 700 }}>Fraud Detection</h1>
          <Link to="/" style={{ color: '#dfe6e9', textDecoration: 'none' }}>Dashboard</Link>
          <Link to="/test" style={{ color: '#dfe6e9', textDecoration: 'none' }}>Test Transaction</Link>
          <Link to="/bulk" style={{ color: '#dfe6e9', textDecoration: 'none' }}>Bulk Check</Link>
          <Link to="/models" style={{ color: '#dfe6e9', textDecoration: 'none' }}>Models</Link>
        </nav>
        <main style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/test" element={<TestTransaction />} />
            <Route path="/bulk" element={<BulkCheck />} />
            <Route path="/transaction/:id" element={<TransactionDetail />} />
            <Route path="/models" element={<ModelComparison />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
