import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

export const analyzeArticle = (data) => api.post('/analyze', data)
export const getDashboard = (params) => api.get('/dashboard', { params })
export const getPredictionDetail = (id) => api.get(`/predictions/${id}`)
export const submitFeedback = (data) => api.post('/feedback', data)
export const batchAnalyze = (formData) =>
  api.post('/batch/analyze', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
export const getBatchJobs = () => api.get('/batch/jobs')
export const getSources = () => api.get('/sources')
export const getMetrics = () => api.get('/metrics')
export const triggerTrain = () => api.post('/train')
export const getHealth = () => axios.get('/health')
export const exportCSV = (params = {}) => {
  const query = new URLSearchParams(params).toString()
  return `/api/v1/export/csv${query ? `?${query}` : ''}`
}

export default api
