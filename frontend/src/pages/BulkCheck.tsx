import { useState } from 'react'
import { ArrowLeft, Upload, Download, AlertTriangle } from 'lucide-react'
import { Link } from 'react-router-dom'

interface BatchPrediction {
  transaction_id: string
  merchant_id: string
  amount: number
  confidence: number
  label: string
  top_features: Array<{ feature: string; contribution: number }>
  model_version: string
}

interface BatchResult {
  success: boolean
  total_transactions: number
  fraud_detected: number
  legitimate: number
  fraud_rate: number
  model_version: string
  predictions: BatchPrediction[]
}

export default function BulkCheck() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<BatchResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragOver, setDragOver] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
      setResult(null)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile)
        setError(null)
        setResult(null)
      } else {
        setError('Please upload a CSV file')
      }
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = () => {
    setDragOver(false)
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file')
      return
    }

    setUploading(true)
    setError(null)

    try {
      // Read CSV file
      const text = await file.text()
      const lines = text.split('\n').filter(l => l.trim())

      if (lines.length < 2) {
        throw new Error('CSV file is empty or invalid')
      }

      // Parse CSV (skip header)
      const predictions: BatchPrediction[] = []
      let fraudCount = 0
      let legitCount = 0

      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

      // Process each transaction
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim()
        if (!line) continue

        const fields = line.split(',')
        if (fields.length < 12) continue

        // Parse CSV row
        const transaction = {
          merchant_id: fields[0] || 'MERCHANT',
          amount: parseFloat(fields[1]) || 0,
          currency: fields[2] || 'USD',
          payment_method: fields[3] || 'credit_card',
          user_id_hash: fields[4] || 'user_' + i,
          ip_hash: fields[5] || '192.168.1.1',
          email_domain: fields[6] || 'example.com',
          is_new_user: fields[7]?.toLowerCase() === 'true',
          device_type: fields[8] || 'desktop',
          billing_shipping_match: fields[9]?.toLowerCase() !== 'false',
          hour_of_day: parseInt(fields[10]) || 12,
          day_of_week: parseInt(fields[11]) || 1,
          items_count: parseInt(fields[12]) || 1
        }

        // Call prediction API
        const response = await fetch(`${API_URL}/predict`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(transaction)
        })

        if (response.ok) {
          const prediction = await response.json()
          predictions.push({
            transaction_id: `TXN_${i}`,
            merchant_id: transaction.merchant_id,
            amount: transaction.amount,
            confidence: prediction.confidence,
            label: prediction.label,
            top_features: prediction.top_features,
            model_version: '2.0.0'
          })

          if (prediction.label === 'HIGH RISK') fraudCount++
          else legitCount++
        }
      }

      setResult({
        success: true,
        total_transactions: predictions.length,
        fraud_detected: fraudCount,
        legitimate: legitCount,
        fraud_rate: predictions.length > 0 ? (fraudCount / predictions.length) * 100 : 0,
        model_version: '2.0.0',
        predictions
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setUploading(false)
    }
  }

  const exportToCSV = () => {
    if (!result) return

    const headers = [
      'Transaction ID',
      'Merchant ID',
      'Amount',
      'Verdict',
      'Confidence (%)',
      'Model Version',
      'Top Feature 1',
      'Top Feature 2',
      'Top Feature 3',
    ]

    const rows = result.predictions.map((p) => {
      const features = p.top_features || []
      const riskLabel = p.label // Already 'HIGH RISK' or 'LOW RISK' from API
      return [
        p.transaction_id,
        p.merchant_id,
        p.amount.toFixed(2),
        riskLabel,
        (p.confidence * 100).toFixed(1),
        p.model_version,
        features[0] ? `${features[0].feature}: ${features[0].contribution.toFixed(4)}` : '',
        features[1] ? `${features[1].feature}: ${features[1].contribution.toFixed(4)}` : '',
        features[2] ? `${features[2].feature}: ${features[2].contribution.toFixed(4)}` : '',
      ]
    })

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.setAttribute('href', URL.createObjectURL(blob))
    link.setAttribute('download', `bulk_fraud_check_${new Date().toISOString().split('T')[0]}.csv`)
    link.click()
  }

  const downloadTemplate = () => {
    const template = `merchant_id,amount,currency,payment_method,user_id_hash,ip_hash,email_domain,is_new_user,device_type,billing_shipping_match,hour_of_day,day_of_week,items_count
merchant_001,250.50,USD,credit_card,user123hash,192.168.1.1hash,gmail.com,false,desktop,true,14,3,5
merchant_002,5000.00,USD,paypal,user456hash,10.0.0.1hash,yahoo.com,true,mobile,false,3,0,1
merchant_003,45.99,USD,debit_card,user789hash,172.16.0.1hash,outlook.com,false,tablet,true,10,5,3`

    const blob = new Blob([template], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.setAttribute('href', URL.createObjectURL(blob))
    link.setAttribute('download', 'bulk_check_template.csv')
    link.click()
  }

  return (
    <div style={{ padding: '40px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '30px' }}>
        <Link
          to="/"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            color: '#3b82f6',
            textDecoration: 'none',
            marginBottom: '16px',
            fontSize: '14px',
          }}
        >
          <ArrowLeft size={16} />
          Back to Dashboard
        </Link>
        <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>
          Bulk Transaction Check
        </h1>
        <p style={{ color: '#6b7280', fontSize: '16px' }}>
          Upload a CSV file to check multiple transactions at once
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
        {/* Left Column - Upload */}
        <div>
          {/* Upload Card */}
          <div
            style={{
              background: 'white',
              borderRadius: '12px',
              padding: '30px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              marginBottom: '20px',
            }}
          >
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px' }}>
              Upload CSV File
            </h2>

            {/* Drag and Drop Zone */}
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              style={{
                border: dragOver ? '2px dashed #3b82f6' : '2px dashed #d1d5db',
                borderRadius: '8px',
                padding: '40px',
                textAlign: 'center',
                background: dragOver ? '#eff6ff' : '#f9fafb',
                marginBottom: '20px',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onClick={() => document.getElementById('fileInput')?.click()}
            >
              <Upload
                size={48}
                style={{ margin: '0 auto 16px', color: dragOver ? '#3b82f6' : '#9ca3af' }}
              />
              <p style={{ fontSize: '16px', color: '#374151', marginBottom: '8px' }}>
                {file ? file.name : 'Drag and drop your CSV file here'}
              </p>
              <p style={{ fontSize: '14px', color: '#6b7280' }}>or click to browse</p>
              <input
                id="fileInput"
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </div>

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              style={{
                width: '100%',
                padding: '12px',
                background: !file || uploading ? '#d1d5db' : '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: !file || uploading ? 'not-allowed' : 'pointer',
                marginBottom: '12px',
              }}
            >
              {uploading ? 'Processing...' : 'Check Transactions'}
            </button>

            {/* Download Template */}
            <button
              onClick={downloadTemplate}
              style={{
                width: '100%',
                padding: '12px',
                background: 'white',
                color: '#3b82f6',
                border: '1px solid #3b82f6',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
              }}
            >
              <Download size={16} />
              Download CSV Template
            </button>
          </div>

          {/* CSV Format Guide */}
          <div
            style={{
              background: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            }}
          >
            <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px' }}>
              CSV Format Requirements
            </h3>
            <div style={{ fontSize: '14px', color: '#4b5563', lineHeight: '1.8' }}>
              <p style={{ marginBottom: '12px' }}>
                <strong>Required Columns:</strong>
              </p>
              <ul style={{ marginLeft: '20px', marginBottom: '16px' }}>
                <li>merchant_id</li>
                <li>amount</li>
                <li>payment_method</li>
                <li>user_id_hash</li>
                <li>ip_hash</li>
                <li>email_domain</li>
                <li>is_new_user (true/false)</li>
                <li>device_type</li>
                <li>billing_shipping_match (true/false)</li>
                <li>hour_of_day (0-23)</li>
                <li>day_of_week (0-6)</li>
                <li>items_count</li>
              </ul>
              <p style={{ marginBottom: '8px' }}>
                <strong>Optional:</strong>
              </p>
              <ul style={{ marginLeft: '20px' }}>
                <li>transaction_id (auto-generated if missing)</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Right Column - Results */}
        <div>
          {error && (
            <div
              style={{
                background: '#fef2f2',
                border: '1px solid #fecaca',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
              }}
            >
              <AlertTriangle size={20} style={{ color: '#dc2626' }} />
              <p style={{ color: '#dc2626', fontSize: '14px' }}>{error}</p>
            </div>
          )}

          {result && (
            <>
              {/* Summary Cards */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '16px',
                  marginBottom: '20px',
                }}
              >
                <div
                  style={{
                    background: 'white',
                    borderRadius: '12px',
                    padding: '20px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  }}
                >
                  <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
                    Total Transactions
                  </p>
                  <p style={{ fontSize: '28px', fontWeight: 'bold' }}>
                    {result.total_transactions}
                  </p>
                </div>

                <div
                  style={{
                    background: 'white',
                    borderRadius: '12px',
                    padding: '20px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  }}
                >
                  <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
                    Fraud Rate
                  </p>
                  <p style={{ fontSize: '28px', fontWeight: 'bold', color: '#dc2626' }}>
                    {result.fraud_rate.toFixed(1)}%
                  </p>
                </div>

                <div
                  style={{
                    background: 'white',
                    borderRadius: '12px',
                    padding: '20px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  }}
                >
                  <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
                    High Risk
                  </p>
                  <p style={{ fontSize: '28px', fontWeight: 'bold', color: '#dc2626' }}>
                    {result.fraud_detected}
                  </p>
                </div>

                <div
                  style={{
                    background: 'white',
                    borderRadius: '12px',
                    padding: '20px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  }}
                >
                  <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
                    Low Risk
                  </p>
                  <p style={{ fontSize: '28px', fontWeight: 'bold', color: '#10b981' }}>
                    {result.legitimate}
                  </p>
                </div>
              </div>

              {/* Results Table */}
              <div
                style={{
                  background: 'white',
                  borderRadius: '12px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    padding: '20px',
                    borderBottom: '1px solid #e5e7eb',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <h3 style={{ fontSize: '18px', fontWeight: '600' }}>
                    Results ({result.predictions.length})
                  </h3>
                  <button
                    onClick={exportToCSV}
                    style={{
                      padding: '8px 16px',
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '14px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                  >
                    <Download size={16} />
                    Export CSV
                  </button>
                </div>

                {/* Table */}
                <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead
                      style={{
                        background: '#f9fafb',
                        position: 'sticky',
                        top: 0,
                        zIndex: 10,
                      }}
                    >
                      <tr>
                        <th
                          style={{
                            padding: '12px 16px',
                            textAlign: 'left',
                            fontSize: '12px',
                            fontWeight: '600',
                            color: '#6b7280',
                            borderBottom: '1px solid #e5e7eb',
                          }}
                        >
                          Transaction ID
                        </th>
                        <th
                          style={{
                            padding: '12px 16px',
                            textAlign: 'left',
                            fontSize: '12px',
                            fontWeight: '600',
                            color: '#6b7280',
                            borderBottom: '1px solid #e5e7eb',
                          }}
                        >
                          Amount
                        </th>
                        <th
                          style={{
                            padding: '12px 16px',
                            textAlign: 'left',
                            fontSize: '12px',
                            fontWeight: '600',
                            color: '#6b7280',
                            borderBottom: '1px solid #e5e7eb',
                          }}
                        >
                          Verdict
                        </th>
                        <th
                          style={{
                            padding: '12px 16px',
                            textAlign: 'left',
                            fontSize: '12px',
                            fontWeight: '600',
                            color: '#6b7280',
                            borderBottom: '1px solid #e5e7eb',
                          }}
                        >
                          Confidence
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.predictions.map((pred, idx) => (
                        <tr
                          key={idx}
                          style={{
                            borderBottom: '1px solid #f3f4f6',
                            background: idx % 2 === 0 ? 'white' : '#fafafa',
                          }}
                        >
                          <td
                            style={{
                              padding: '12px 16px',
                              fontSize: '14px',
                              fontFamily: 'monospace',
                            }}
                          >
                            {pred.transaction_id}
                          </td>
                          <td style={{ padding: '12px 16px', fontSize: '14px' }}>
                            ${pred.amount.toFixed(2)}
                          </td>
                          <td style={{ padding: '12px 16px' }}>
                            <span
                              style={{
                                padding: '4px 12px',
                                borderRadius: '12px',
                                fontSize: '12px',
                                fontWeight: '600',
                                background:
                                  pred.label.toLowerCase() === 'fraud' ? '#fef2f2' : '#f0fdf4',
                                color: pred.label.toLowerCase() === 'fraud' ? '#dc2626' : '#10b981',
                              }}
                            >
                              {pred.label.toLowerCase() === 'fraud' ? 'HIGH RISK' : 'LOW RISK'}
                            </span>
                          </td>
                          <td style={{ padding: '12px 16px', fontSize: '14px' }}>
                            {(pred.confidence * 100).toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {!result && !error && (
            <div
              style={{
                background: 'white',
                borderRadius: '12px',
                padding: '60px 40px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                textAlign: 'center',
              }}
            >
              <Upload size={64} style={{ margin: '0 auto 20px', color: '#d1d5db' }} />
              <p style={{ fontSize: '18px', color: '#6b7280', marginBottom: '8px' }}>
                No results yet
              </p>
              <p style={{ fontSize: '14px', color: '#9ca3af' }}>
                Upload a CSV file to get started
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
