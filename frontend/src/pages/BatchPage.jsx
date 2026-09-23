import { useState, useEffect, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { UploadCloud, FileText, CheckCircle2, AlertCircle, RefreshCw, Download } from 'lucide-react'
import Card, { CardTitle } from '../components/Card'
import { batchAnalyze, getBatchJobs } from '../api/client'
import styles from './BatchPage.module.css'

export default function BatchPage() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)

  const loadJobs = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getBatchJobs()
      setJobs(res.data || [])
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadJobs()
  }, [loadJobs])

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploading(true)
    const tid = toast.loading(`Uploading and processing ${file.name}...`)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await batchAnalyze(formData)
      toast.success(
        `Batch complete! Analyzed ${res.data.processed_items} items: ${res.data.fake_count} FAKE, ${res.data.real_count} REAL`,
        { id: tid, duration: 6000 }
      )
      loadJobs()
    } catch (e) {
      toast.error(`Batch analysis failed: ${e.response?.data?.detail || e.message}`, { id: tid })
    } finally {
      setUploading(false)
    }
  }, [loadJobs])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'], 'text/plain': ['.txt'] },
    maxFiles: 1,
    disabled: uploading
  })

  const downloadSampleCsv = () => {
    const csvContent =
      'title,text,source,author,url\n' +
      '"Miracle Cure Discovery","BOMBSHELL! The government is suppressing a secret natural cure for all diseases! Share now!","infowars.com","Anonymous","http://fake.news/1"\n' +
      '"Economic Report 2026","The central bank held rates steady today following moderate growth in consumer spending according to quarterly metrics.","reuters.com","Jane Smith","http://reuters.com/news/1"'
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'sample_news_batch.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className={styles.container}>
      <Card glow>
        <CardTitle icon={UploadCloud}>Upload Dataset for Bulk Misinformation Scoring</CardTitle>

        <div
          {...getRootProps()}
          className={`${styles.dropzone} ${isDragActive ? styles.dropzoneActive : ''}`}
        >
          <input {...getInputProps()} />
          <div className={styles.dropIcon}>
            <UploadCloud size={28} />
          </div>
          <div className={styles.dropTitle}>
            {uploading ? 'Processing batch with NLP pipeline...' : isDragActive ? 'Drop your CSV file here' : 'Drag & Drop CSV file here, or click to browse'}
          </div>
          <p className={styles.dropSub}>
            Supports standard news datasets (LIAR, ISOT, FakeNewsNet format). Required column: <code>text</code>. Optional: <code>title</code>, <code>source</code>, <code>author</code>, <code>url</code>.
          </p>

          <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
            <span className={styles.sampleNote}>Expected format: .csv or .tsv</span>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); downloadSampleCsv(); }}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--primary-light)',
                cursor: 'pointer',
                fontSize: '0.78rem',
                textDecoration: 'underline',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 4
              }}
            >
              <Download size={13} /> Download Template
            </button>
          </div>
        </div>
      </Card>

      {/* ── Batch Jobs History ── */}
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <CardTitle icon={FileText} style={{ marginBottom: 0 }}>Recent Batch Processing Runs</CardTitle>
          <button
            onClick={loadJobs}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
          >
            <RefreshCw size={15} />
          </button>
        </div>

        {jobs.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '24px 0' }}>
            No batch jobs recorded yet. Upload a CSV above to run bulk classification.
          </p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className={styles.jobsTable}>
              <thead>
                <tr>
                  <th>Job ID</th>
                  <th>Status</th>
                  <th>Total Rows</th>
                  <th>Flagged Fake</th>
                  <th>Credible Real</th>
                  <th>Uncertain</th>
                  <th>Date & Time</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((j) => (
                  <tr key={j.batch_id}>
                    <td style={{ fontFamily: 'var(--mono)', fontSize: '0.78rem' }}>{j.batch_id.slice(0, 8)}...</td>
                    <td>
                      <span className={`${styles.pill} ${j.status === 'completed' ? styles.pillSuccess : styles.pillRunning}`}>
                        {j.status.toUpperCase()}
                      </span>
                    </td>
                    <td>{j.processed_items} / {j.total_items}</td>
                    <td style={{ color: 'var(--fake)', fontWeight: 600 }}>{j.fake_count}</td>
                    <td style={{ color: 'var(--real)', fontWeight: 600 }}>{j.real_count}</td>
                    <td style={{ color: 'var(--uncertain)', fontWeight: 600 }}>{j.uncertain_count}</td>
                    <td style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                      {new Date(j.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}
