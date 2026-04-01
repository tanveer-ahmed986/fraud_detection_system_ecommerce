import { Link } from 'react-router-dom'
import { Shield, TestTube, Upload, Activity } from 'lucide-react'

export default function Home() {
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      {/* Hero Section */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '16px',
        padding: '60px 40px',
        color: '#fff',
        textAlign: 'center',
        marginBottom: '48px'
      }}>
        <Shield size={64} style={{ marginBottom: '24px', opacity: 0.9 }} />
        <h1 style={{ fontSize: '42px', fontWeight: 700, marginBottom: '16px' }}>
          FraudShield AI
        </h1>
        <p style={{ fontSize: '20px', opacity: 0.95, maxWidth: '700px', margin: '0 auto' }}>
          AI-powered risk assessment for e-commerce. Real-time transaction analysis
          with 90%+ detection accuracy and explainable AI insights.
        </p>
      </div>

      {/* Features Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '24px',
        marginBottom: '48px'
      }}>
        {/* Test Single Transaction */}
        <Link to="/test" style={{ textDecoration: 'none' }}>
          <div style={{
            background: '#fff',
            borderRadius: '12px',
            padding: '32px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
            cursor: 'pointer',
            transition: 'transform 0.2s, box-shadow 0.2s'
          }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)'
              e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.12)'
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)'
            }}
          >
            <TestTube size={40} color="#667eea" style={{ marginBottom: '16px' }} />
            <h3 style={{ fontSize: '20px', fontWeight: 600, color: '#2d3436', marginBottom: '12px' }}>
              Risk Analysis
            </h3>
            <p style={{ color: '#636e72', lineHeight: 1.6 }}>
              Analyze individual transactions in real-time. Get instant risk assessment
              with confidence scores and explainable AI insights.
            </p>
            <div style={{
              marginTop: '20px',
              color: '#667eea',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              Try it now →
            </div>
          </div>
        </Link>

        {/* Bulk CSV Check */}
        <Link to="/bulk" style={{ textDecoration: 'none' }}>
          <div style={{
            background: '#fff',
            borderRadius: '12px',
            padding: '32px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
            cursor: 'pointer',
            transition: 'transform 0.2s, box-shadow 0.2s'
          }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)'
              e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.12)'
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)'
            }}
          >
            <Upload size={40} color="#00b894" style={{ marginBottom: '16px' }} />
            <h3 style={{ fontSize: '20px', fontWeight: 600, color: '#2d3436', marginBottom: '12px' }}>
              Batch Processing
            </h3>
            <p style={{ color: '#636e72', lineHeight: 1.6 }}>
              Upload CSV files with multiple transactions for bulk risk assessment.
              Get comprehensive analysis with downloadable results and statistics.
            </p>
            <div style={{
              marginTop: '20px',
              color: '#00b894',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              Upload CSV →
            </div>
          </div>
        </Link>

        {/* API Status */}
        <Link to="/status" style={{ textDecoration: 'none' }}>
          <div style={{
            background: '#fff',
            borderRadius: '12px',
            padding: '32px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
            cursor: 'pointer',
            transition: 'transform 0.2s, box-shadow 0.2s'
          }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)'
              e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.12)'
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)'
            }}
          >
            <Activity size={40} color="#fdcb6e" style={{ marginBottom: '16px' }} />
            <h3 style={{ fontSize: '20px', fontWeight: 600, color: '#2d3436', marginBottom: '12px' }}>
              System Status
            </h3>
            <p style={{ color: '#636e72', lineHeight: 1.6 }}>
              Check API health, model status, and system performance metrics.
              See latency and uptime statistics.
            </p>
            <div style={{
              marginTop: '20px',
              color: '#fdcb6e',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              View status →
            </div>
          </div>
        </Link>
      </div>

      {/* Technical Specs */}
      <div style={{
        background: '#fff',
        borderRadius: '12px',
        padding: '40px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        marginBottom: '48px'
      }}>
        <h2 style={{ fontSize: '28px', fontWeight: 700, color: '#2d3436', marginBottom: '32px', textAlign: 'center' }}>
          System Capabilities
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '32px',
          textAlign: 'center'
        }}>
          <div>
            <div style={{ fontSize: '36px', fontWeight: 700, color: '#667eea', marginBottom: '8px' }}>
              90%+
            </div>
            <div style={{ color: '#636e72', fontSize: '14px' }}>
              Recall Rate
            </div>
          </div>
          <div>
            <div style={{ fontSize: '36px', fontWeight: 700, color: '#00b894', marginBottom: '8px' }}>
              &lt;5ms
            </div>
            <div style={{ color: '#636e72', fontSize: '14px' }}>
              Avg Latency
            </div>
          </div>
          <div>
            <div style={{ fontSize: '36px', fontWeight: 700, color: '#fdcb6e', marginBottom: '8px' }}>
              &lt;5%
            </div>
            <div style={{ color: '#636e72', fontSize: '14px' }}>
              False Positive Rate
            </div>
          </div>
          <div>
            <div style={{ fontSize: '36px', fontWeight: 700, color: "#e17055", marginBottom: '8px' }}>
              20+
            </div>
            <div style={{ color: '#636e72', fontSize: '14px' }}>
              ML Features
            </div>
          </div>
        </div>
      </div>

      {/* Tech Stack */}
      <div style={{
        background: '#f8f9fa',
        borderRadius: '12px',
        padding: '40px',
        textAlign: 'center'
      }}>
        <h3 style={{ fontSize: '20px', fontWeight: 600, color: '#2d3436', marginBottom: '24px' }}>
          Built With
        </h3>
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: '16px'
        }}>
          {['Python', 'FastAPI', 'XGBoost', 'scikit-learn', 'React', 'TypeScript', 'Railway', 'Vercel'].map(tech => (
            <span key={tech} style={{
              padding: '8px 16px',
              background: '#fff',
              borderRadius: '20px',
              fontSize: '14px',
              fontWeight: 500,
              color: '#636e72',
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
            }}>
              {tech}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
