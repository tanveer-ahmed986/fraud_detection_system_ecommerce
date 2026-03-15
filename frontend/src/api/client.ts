import axios from 'axios'

// Use relative URL - Vercel will proxy to backend
const api = axios.create({ baseURL: '/api/v1' })

export const getHealth = () => api.get('/health')

export interface DashboardSummary {
  total_predictions: number
  fraud_count: number
  legitimate_count: number
  fraud_rate: number
  avg_confidence: number
  model_version: string
  model_recall: number | null
  model_precision: number | null
  model_fpr: number | null
}

export interface TimeseriesPoint {
  date: string
  total: number
  fraud: number
  fraud_rate: number
}

export interface PredictionItem {
  transaction_id: string
  amount: number
  label: string
  confidence: number
  merchant_id: string
  created_at: string
  top_features: { feature: string; contribution: number }[]
}

export interface ModelInfo {
  version: string
  is_active: boolean
  recall: number
  precision: number
  f1_score: number
  fpr: number
  dataset_rows: number
  created_at: string
}

export interface TransactionDetail {
  transaction_id: string
  amount: number
  merchant_id: string
  payment_method: string
  user_id_hash: string
  ip_hash: string
  email_domain: string
  is_new_user: boolean
  device_type: string
  billing_shipping_match: boolean
  hour_of_day: number
  day_of_week: number
  items_count: number
  created_at: string
  label: string
  confidence: number
  threshold_used: number
  model_version: string
  latency_ms: number
  top_features: { feature: string; contribution: number }[]
  prediction_created_at: string
}

export const getSummary = () => api.get<DashboardSummary>('/dashboard/summary')
export const getTimeseries = (days = 30) => api.get<TimeseriesPoint[]>(`/dashboard/timeseries?days=${days}`)
export const getPredictions = (page = 1, pageSize = 20) =>
  api.get<{ total: number; predictions: PredictionItem[] }>(`/dashboard/predictions?page=${page}&page_size=${pageSize}`)
export const getTransaction = (id: string) => api.get<TransactionDetail>(`/dashboard/transaction/${id}`)
export const getModels = () => api.get<ModelInfo[]>('/models')

// Predict API
export interface PredictRequest {
  merchant_id: string
  amount: number
  payment_method: string
  user_id_hash: string
  ip_hash: string
  email_domain: string
  is_new_user: boolean
  device_type: string
  billing_shipping_match: boolean
  hour_of_day: number
  day_of_week: number
  items_count: number
}

export interface PredictResponse {
  transaction_id: string
  label: string
  confidence: number
  threshold_used: number
  top_features: { feature: string; contribution: number }[]
  latency_ms: number
  fallback_applied: boolean
}

export const predictTransaction = (data: PredictRequest) =>
  api.post<PredictResponse>('/predict', data)

export default api
