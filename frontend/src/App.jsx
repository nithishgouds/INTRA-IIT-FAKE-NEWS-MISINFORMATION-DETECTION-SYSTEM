import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import AnalyzePage from './pages/AnalyzePage'
import DashboardPage from './pages/DashboardPage'
import BatchPage from './pages/BatchPage'
import SourcesPage from './pages/SourcesPage'
import MetricsPage from './pages/MetricsPage'

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#111827',
            color: '#f1f5f9',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '10px',
            fontSize: '0.82rem',
          },
          success: { iconTheme: { primary: '#22c55e', secondary: '#111827' } },
          error: { iconTheme: { primary: '#ef4444', secondary: '#111827' } },
        }}
      />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/analyze" replace />} />
          <Route path="analyze" element={<AnalyzePage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="batch" element={<BatchPage />} />
          <Route path="sources" element={<SourcesPage />} />
          <Route path="metrics" element={<MetricsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
