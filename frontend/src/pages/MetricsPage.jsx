import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { BarChart2, RefreshCw, Zap, AlertCircle, CheckCircle } from 'lucide-react'
import Card, { CardTitle } from '../components/Card'
import { getMetrics, triggerTrain } from '../api/client'
import styles from './MetricsPage.module.css'

export default function MetricsPage() {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [retraining, setRetraining] = useState(false)

  async function loadMetrics() {
    setLoading(true)
    try {
      const res = await getMetrics()
      setMetrics(res.data)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMetrics()
  }, [])

  async function handleRetrain() {
    setRetraining(true)
    const tid = toast.loading('Retraining model on training dataset & confirmed feedback...')
    try {
      const res = await triggerTrain()
      toast.success(
        `Model retrained! New Acc: ${(res.data.metrics?.accuracy * 100).toFixed(1)}%`,
        { id: tid }
      )
      loadMetrics()
    } catch (e) {
      toast.error(`Retrain failed: ${e.response?.data?.detail || e.message}`, { id: tid })
    } finally {
      setRetraining(false)
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
        <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite' }} />
        <p style={{ marginTop: 12 }}>Loading evaluation metrics...</p>
      </div>
    )
  }

  const m = metrics || {}
  const cm = m.confusion_matrix || [[0, 0], [0, 0]]
  const tn = cm[0]?.[0] ?? 0
  const fp = cm[0]?.[1] ?? 0
  const fn = cm[1]?.[0] ?? 0
  const tp = cm[1]?.[1] ?? 0

  return (
    <div className={styles.container}>
      {/* ── Retrain Action Banner ── */}
      <Card glow>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <CardTitle icon={Zap} style={{ marginBottom: 4 }}>Continuous Model Optimization</CardTitle>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
              Integrates human feedback (confirmed/relabeled) with linguistic feature extraction to update model weights.
            </p>
          </div>
          <button
            onClick={handleRetrain}
            disabled={retraining}
            style={{
              background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
              color: '#fff',
              border: 'none',
              padding: '10px 20px',
              borderRadius: 'var(--radius-sm)',
              fontWeight: 700,
              fontSize: '0.85rem',
              cursor: retraining ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              opacity: retraining ? 0.7 : 1
            }}
          >
            <RefreshCw size={15} style={retraining ? { animation: 'spin 1s linear infinite' } : {}} />
            {retraining ? 'Retraining...' : 'Trigger Pipeline Retrain'}
          </button>
        </div>
      </Card>

      {/* ── Key Metrics Cards ── */}
      <div className={styles.metricsGrid}>
        <div className={styles.metricCard}>
          <div className={styles.metricVal}>
            {m.accuracy != null ? `${(m.accuracy * 100).toFixed(1)}%` : '—'}
          </div>
          <div className={styles.metricName}>Accuracy</div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricVal}>
            {m.f1_score != null ? `${(m.f1_score * 100).toFixed(1)}%` : '—'}
          </div>
          <div className={styles.metricName}>F1 Score</div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricVal}>
            {m.precision != null ? `${(m.precision * 100).toFixed(1)}%` : '—'}
          </div>
          <div className={styles.metricName}>Precision</div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricVal}>
            {m.recall != null ? `${(m.recall * 100).toFixed(1)}%` : '—'}
          </div>
          <div className={styles.metricName}>Recall</div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricVal}>
            {m.auc_roc != null ? `${(m.auc_roc * 100).toFixed(1)}%` : '—'}
          </div>
          <div className={styles.metricName}>ROC-AUC</div>
        </div>
      </div>

      {/* ── Confusion Matrix ── */}
      <Card>
        <CardTitle icon={BarChart2}>Confusion Matrix (Validation Split)</CardTitle>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
          Tested on holdout split of {m.total_samples ?? 0} samples ({m.fake_samples ?? 0} Fake, {m.real_samples ?? 0} Real)
        </p>

        <div className={styles.matrixGrid}>
          <div className={styles.matrixCell} style={{ background: 'var(--real-bg)', borderColor: 'var(--real-border)' }}>
            <div className={styles.cellVal} style={{ color: 'var(--real)' }}>{tp}</div>
            <div className={styles.cellLabel}>True Positives (Fake detected)</div>
          </div>

          <div className={styles.matrixCell} style={{ background: 'var(--fake-bg)', borderColor: 'var(--fake-border)' }}>
            <div className={styles.cellVal} style={{ color: 'var(--fake)' }}>{fp}</div>
            <div className={styles.cellLabel}>False Positives (Real misflagged)</div>
          </div>

          <div className={styles.matrixCell} style={{ background: 'var(--fake-bg)', borderColor: 'var(--fake-border)' }}>
            <div className={styles.cellVal} style={{ color: 'var(--fake)' }}>{fn}</div>
            <div className={styles.cellLabel}>False Negatives (Fake missed)</div>
          </div>

          <div className={styles.matrixCell} style={{ background: 'var(--real-bg)', borderColor: 'var(--real-border)' }}>
            <div className={styles.cellVal} style={{ color: 'var(--real)' }}>{tn}</div>
            <div className={styles.cellLabel}>True Negatives (Real verified)</div>
          </div>
        </div>
      </Card>

      {/* ── Error & Failure Analysis ── */}
      <Card>
        <CardTitle icon={AlertCircle}>Failure Analysis & Error Cases</CardTitle>
        <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginBottom: 16 }}>
          Reviewing borderline and misclassified cases enables targeted prompt/feature adjustments and synthetic data augmentation.
        </p>

        {(!m.false_positives_sample?.length && !m.false_negatives_sample?.length) ? (
          <div style={{ textAlign: 'center', padding: '20px 0', color: 'var(--real)' }}>
            <CheckCircle size={28} style={{ margin: '0 auto 8px' }} />
            <p style={{ fontWeight: 600 }}>Zero error cases in current validation batch!</p>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>All test samples were correctly classified.</p>
          </div>
        ) : (
          <div className={styles.sampleList}>
            {m.false_positives_sample?.map((s, i) => (
              <div key={i} className={styles.sampleItem}>
                <span style={{ color: 'var(--fake)', fontWeight: 700, fontSize: '0.78rem' }}>[False Positive] </span>
                <span style={{ color: 'var(--text-secondary)' }}>{s.text}</span>
              </div>
            ))}
            {m.false_negatives_sample?.map((s, i) => (
              <div key={i} className={styles.sampleItem}>
                <span style={{ color: 'var(--uncertain)', fontWeight: 700, fontSize: '0.78rem' }}>[False Negative] </span>
                <span style={{ color: 'var(--text-secondary)' }}>{s.text}</span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
