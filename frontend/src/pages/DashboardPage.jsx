import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  LayoutDashboard, CheckCircle, AlertTriangle, HelpCircle,
  Download, Filter, RefreshCw, Eye, MessageSquare, Clock, User, Globe
} from 'lucide-react'
import Card from '../components/Card'
import { getDashboard, submitFeedback, exportCSV } from '../api/client'
import styles from './DashboardPage.module.css'

export default function DashboardPage() {
  const [data, setData] = useState({ items: [], stats: {}, total: 0 })
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [labelFilter, setLabelFilter] = useState('')
  const [sortBy, setSortBy] = useState('date_desc')
  const [page, setPage] = useState(1)
  const [selectedItem, setSelectedItem] = useState(null)
  const [relabelNote, setRelabelNote] = useState('')

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getDashboard({
        page,
        page_size: 15,
        status_filter: statusFilter || undefined,
        label_filter: labelFilter || undefined,
        sort_by: sortBy,
      })
      setData(res.data)
    } catch (e) {
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }, [page, statusFilter, labelFilter, sortBy])

  useEffect(() => {
    loadData()
  }, [loadData])

  async function handleFeedback(predictionId, action, assignedLabel = null) {
    try {
      await submitFeedback({
        prediction_id: predictionId,
        action,
        assigned_label: assignedLabel,
        note: relabelNote || `Review action: ${action}`,
        reviewer: 'analyst_ui'
      })
      toast.success(`Marked as ${action.toUpperCase()}`)
      setSelectedItem(null)
      setRelabelNote('')
      loadData()
    } catch (e) {
      toast.error('Failed to submit feedback')
    }
  }

  const { stats = {} } = data

  return (
    <div className={styles.container}>
      {/* ── Stats Row ── */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: 'rgba(99,102,241,0.15)', color: 'var(--primary-light)' }}>
            <LayoutDashboard size={22} />
          </div>
          <div>
            <div className={styles.statValue}>{stats.total_analyzed ?? 0}</div>
            <div className={styles.statLabel}>Total Analyzed</div>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: 'rgba(239,68,68,0.15)', color: 'var(--fake)' }}>
            <AlertTriangle size={22} />
          </div>
          <div>
            <div className={styles.statValue}>{stats.fake_count ?? 0}</div>
            <div className={styles.statLabel}>Flagged Misinformation</div>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: 'rgba(245,158,11,0.15)', color: 'var(--uncertain)' }}>
            <HelpCircle size={22} />
          </div>
          <div>
            <div className={styles.statValue}>{stats.pending_review ?? 0}</div>
            <div className={styles.statLabel}>Pending Review</div>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: 'rgba(34,197,94,0.15)', color: 'var(--real)' }}>
            <CheckCircle size={22} />
          </div>
          <div>
            <div className={styles.statValue}>{stats.reviewed_count ?? 0}</div>
            <div className={styles.statLabel}>Reviewed by Human</div>
          </div>
        </div>
      </div>

      {/* ── Filter Toolbar ── */}
      <div className={styles.toolbar}>
        <div className={styles.filters}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            <Filter size={15} /> Filters:
          </div>

          <select
            className={styles.select}
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
          >
            <option value="">All Review Statuses</option>
            <option value="pending">Pending Review</option>
            <option value="confirmed">Confirmed Fake</option>
            <option value="dismissed">Dismissed (False Alarm)</option>
            <option value="relabeled">Relabeled</option>
          </select>

          <select
            className={styles.select}
            value={labelFilter}
            onChange={(e) => { setLabelFilter(e.target.value); setPage(1) }}
          >
            <option value="">All Classifications</option>
            <option value="FAKE">FAKE</option>
            <option value="REAL">REAL</option>
            <option value="UNCERTAIN">UNCERTAIN</option>
          </select>

          <select
            className={styles.select}
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="date_desc">Latest First</option>
            <option value="prob_desc">Highest Risk First</option>
            <option value="conf_asc">Lowest Confidence (Triage)</option>
          </select>

          <button
            onClick={loadData}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: 4 }}
            title="Refresh list"
          >
            <RefreshCw size={15} />
          </button>
        </div>

        <a
          href={exportCSV({ status: statusFilter, label: labelFilter })}
          download="truthlens_export.csv"
          className={styles.exportBtn}
        >
          <Download size={14} /> Export CSV
        </a>
      </div>

      {/* ── Content List ── */}
      {loading ? (
        <div className={styles.emptyState}>
          <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite' }} />
          <p style={{ marginTop: 12 }}>Loading queue records...</p>
        </div>
      ) : data.items.length === 0 ? (
        <div className={styles.emptyState}>
          <CheckCircle size={32} style={{ color: 'var(--real)', opacity: 0.8 }} />
          <p style={{ marginTop: 12, fontWeight: 600 }}>No flagged items match your filter criteria.</p>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>You can analyze new articles from the Analyze page or run a batch scan.</p>
        </div>
      ) : (
        <div className={styles.list}>
          {data.items.map((item) => {
            const isFake = item.label === 'FAKE'
            const isReal = item.label === 'REAL'
            const badgeBg = isFake ? 'rgba(239,68,68,0.15)' : isReal ? 'rgba(34,197,94,0.15)' : 'rgba(245,158,11,0.15)'
            const badgeColor = isFake ? 'var(--fake)' : isReal ? 'var(--real)' : 'var(--uncertain)'
            const probPercent = Math.round(item.fake_probability * 100)

            return (
              <motion.div
                key={item.prediction_id}
                className={styles.itemCard}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className={styles.itemHeader}>
                  <div>
                    <h3 className={styles.itemTitle}>{item.title || 'Untitled Article / Post'}</h3>
                    <div className={styles.itemMeta}>
                      {item.source && (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                          <Globe size={12} /> {item.source}
                        </span>
                      )}
                      {item.author && (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                          <User size={12} /> {item.author}
                        </span>
                      )}
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                        <Clock size={12} /> {new Date(item.predicted_at).toLocaleString()}
                      </span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span
                      className={styles.badge}
                      style={{ background: badgeBg, color: badgeColor, border: `1px solid ${badgeColor}` }}
                    >
                      {item.label} ({(item.confidence * 100).toFixed(0)}%)
                    </span>
                    <span
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        padding: '3px 8px',
                        borderRadius: '4px',
                        background: 'rgba(255,255,255,0.06)',
                        color: 'var(--text-secondary)'
                      }}
                    >
                      {item.review_status.toUpperCase()}
                    </span>
                  </div>
                </div>

                <p className={styles.itemText}>{item.text_preview}</p>

                <div className={styles.itemFooter}>
                  <div className={styles.probMeter}>
                    <span>Risk Score:</span>
                    <div className={styles.probBar}>
                      <div
                        className={styles.probFill}
                        style={{
                          width: `${probPercent}%`,
                          background: probPercent > 70 ? 'var(--fake)' : probPercent > 40 ? 'var(--uncertain)' : 'var(--real)'
                        }}
                      />
                    </div>
                    <span>{probPercent}%</span>
                  </div>

                  {/* Human In The Loop Actions */}
                  <div className={styles.actions}>
                    {item.review_status === 'pending' && (
                      <>
                        <button
                          className={`${styles.actionBtn} ${styles.btnConfirm}`}
                          onClick={() => handleFeedback(item.prediction_id, 'confirm')}
                        >
                          Confirm Fake
                        </button>
                        <button
                          className={`${styles.actionBtn} ${styles.btnDismiss}`}
                          onClick={() => handleFeedback(item.prediction_id, 'dismiss')}
                        >
                          Dismiss / Valid
                        </button>
                        <button
                          className={`${styles.actionBtn} ${styles.btnRelabel}`}
                          onClick={() => handleFeedback(item.prediction_id, 'relabel', isFake ? 'REAL' : 'FAKE')}
                        >
                          Invert Label
                        </button>
                      </>
                    )}
                    {item.review_status !== 'pending' && (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Reviewed by human • {item.reviewer_label || item.review_status}
                      </span>
                    )}
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      )}
    </div>
  )
}
