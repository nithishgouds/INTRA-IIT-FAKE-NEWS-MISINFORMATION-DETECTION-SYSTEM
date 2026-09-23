import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  Search, Zap, AlertTriangle, CheckCircle, HelpCircle,
  MessageSquare, ChevronRight, Sparkles, FileText
} from 'lucide-react'
import Card, { CardTitle } from '../components/Card'
import { analyzeArticle, submitFeedback } from '../api/client'
import styles from './AnalyzePage.module.css'

const SAMPLES = {
  real: {
    title: 'Scientists Confirm Climate Research Findings',
    text: `Researchers at the National Oceanic and Atmospheric Administration published findings this week showing that global average temperatures rose by 0.18°C in the past decade. The study, peer-reviewed and published in the journal Nature Climate Change, analyzed data from weather stations across 150 countries. Lead climate scientist Dr. Sarah Chen noted that while the trend is consistent with long-term climate models, local variability remains significant. The findings have been independently verified by three separate research institutions.`,
    source: 'reuters.com',
    author: 'Dr. Sarah Chen',
  },
  fake: {
    title: 'SHOCKING BOMBSHELL: Gov Hiding Secret Cure!!!',
    text: `BREAKING!!! You won't BELIEVE what Big Pharma has been hiding for DECADES!!! SECRET documents EXPOSED show that the government has been SUPPRESSING a natural cure that DESTROYS all disease!!! They are TERRIFIED because this information will BANKRUPT the entire medical industry!!! SHARE THIS IMMEDIATELY before it gets CENSORED!!! The mainstream media REFUSES to cover this BOMBSHELL story because they are all CONTROLLED by the deep state!!!! Wake up people!!! Your health is at stake!!!`,
    source: 'infowars.com',
    author: 'Anonymous',
  },
}

const VERDICT_CONFIG = {
  FAKE: {
    icon: AlertTriangle,
    label: 'Likely Misinformation',
    sublabel: 'High probability of fake or misleading content',
    color: 'var(--fake)',
    bg: 'var(--fake-bg)',
    border: 'var(--fake-border)',
    emoji: '🚨',
  },
  REAL: {
    icon: CheckCircle,
    label: 'Likely Credible',
    sublabel: 'Content appears to be legitimate news',
    color: 'var(--real)',
    bg: 'var(--real-bg)',
    border: 'var(--real-border)',
    emoji: '✅',
  },
  UNCERTAIN: {
    icon: HelpCircle,
    label: 'Uncertain',
    sublabel: 'Low model confidence — requires human review',
    color: 'var(--uncertain)',
    bg: 'var(--uncertain-bg)',
    border: 'var(--uncertain-border)',
    emoji: '⚠️',
  },
}

export default function AnalyzePage() {
  const [form, setForm] = useState({ title: '', text: '', source: '', author: '', url: '' })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [feedbackSent, setFeedbackSent] = useState(false)
  const [showRelabel, setShowRelabel] = useState(false)
  const [relabelVal, setRelabelVal] = useState('REAL')
  const [note, setNote] = useState('')

  const wordCount = form.text.trim() ? form.text.trim().split(/\s+/).length : 0

  const loadSample = (type) => {
    setForm({ ...SAMPLES[type], url: '' })
    setResult(null)
    setFeedbackSent(false)
    setShowRelabel(false)
  }

  const handleSubmit = useCallback(async (e) => {
    e?.preventDefault()
    if (!form.text.trim() || form.text.length < 10) {
      toast.error('Please enter at least 10 characters of text.')
      return
    }
    setLoading(true)
    setResult(null)
    setFeedbackSent(false)
    setShowRelabel(false)
    try {
      const { data } = await analyzeArticle({
        text: form.text,
        title: form.title || null,
        source: form.source || null,
        author: form.author || null,
        url: form.url || null,
      })
      setResult(data)
      toast.success('Analysis complete!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }, [form])

  const handleFeedback = async (action, assignedLabel = null) => {
    if (!result?.prediction?.id) return
    try {
      await submitFeedback({
        prediction_id: result.prediction.id,
        action,
        assigned_label: assignedLabel,
        note: note || null,
        reviewer: 'human_reviewer',
      })
      setFeedbackSent(true)
      setShowRelabel(false)
      toast.success(`Feedback recorded: ${action}`)
    } catch {
      toast.error('Failed to submit feedback')
    }
  }

  const verdict = result ? VERDICT_CONFIG[result.prediction?.label] || VERDICT_CONFIG.UNCERTAIN : null

  return (
    <div className={styles.layout}>
      {/* ─── Input Panel ─── */}
      <Card className={styles.inputCard} glow>
        <CardTitle icon={Search}>Submit Content for Analysis</CardTitle>

        {/* Sample buttons */}
        <div className={styles.sampleRow}>
          <span className={styles.sampleLabel}>Try a sample:</span>
          <button className={`${styles.sampleBtn} ${styles.sampleReal}`} onClick={() => loadSample('real')}>
            <CheckCircle size={12} /> Real News
          </button>
          <button className={`${styles.sampleBtn} ${styles.sampleFake}`} onClick={() => loadSample('fake')}>
            <AlertTriangle size={12} /> Fake News
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className={styles.field}>
            <label className={styles.label}>Headline / Title</label>
            <input
              className={styles.input}
              placeholder="Enter article headline (optional)"
              value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>
              Article Text / Post <span className={styles.required}>*</span>
            </label>
            <textarea
              className={styles.textarea}
              rows={9}
              placeholder="Paste the full article text or social media post here…"
              value={form.text}
              onChange={e => setForm(f => ({ ...f, text: e.target.value }))}
            />
            <div className={styles.charCount}>
              {form.text.length} chars · {wordCount} words · Press Ctrl+Enter to analyze
            </div>
          </div>

          <div className={styles.row2}>
            <div className={styles.field}>
              <label className={styles.label}>Publisher / Source</label>
              <input className={styles.input} placeholder="e.g. reuters.com"
                value={form.source} onChange={e => setForm(f => ({ ...f, source: e.target.value }))} />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>Author</label>
              <input className={styles.input} placeholder="e.g. Jane Smith"
                value={form.author} onChange={e => setForm(f => ({ ...f, author: e.target.value }))} />
            </div>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>URL <span className={styles.optional}>(optional)</span></label>
            <input className={styles.input} type="url" placeholder="https://..."
              value={form.url} onChange={e => setForm(f => ({ ...f, url: e.target.value }))} />
          </div>

          <motion.button
            className={styles.analyzeBtn}
            type="submit"
            disabled={loading}
            whileTap={{ scale: 0.98 }}
          >
            {loading
              ? <><span className={styles.spinner} /> Analyzing…</>
              : <><Search size={16} /> Analyze Content</>
            }
            <span className={styles.shimmer} />
          </motion.button>
        </form>
      </Card>

      {/* ─── Results Panel ─── */}
      <AnimatePresence>
        {result && (
          <motion.div
            className={styles.resultsCol}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.35 }}
          >
            {/* Verdict */}
            <Card className={styles.verdictCard} style={{
              background: verdict.bg,
              borderColor: verdict.border,
            }}>
              <div className={styles.verdictTop}>
                <div className={styles.verdictIconWrap} style={{ background: verdict.bg, borderColor: verdict.border }}>
                  <verdict.icon size={24} style={{ color: verdict.color }} strokeWidth={2} />
                </div>
                <div className={styles.verdictInfo}>
                  <div className={styles.verdictLabel} style={{ color: verdict.color }}>
                    {verdict.label}
                  </div>
                  <div className={styles.verdictSub}>{verdict.sublabel}</div>
                </div>
                <div className={styles.confBadge}>
                  <span className={styles.confVal}>
                    {(result.prediction.confidence * 100).toFixed(1)}%
                  </span>
                  <span className={styles.confLabel}>confidence</span>
                </div>
              </div>

              {/* Probability Bars */}
              <div className={styles.probBars}>
                <ProbBar label="🟢 Real" value={result.prediction.real_probability} color="var(--real)" />
                <ProbBar label="🔴 Fake" value={result.prediction.fake_probability} color="var(--fake)" />
              </div>

              <div className={styles.disclaimer}>
                ⚠️ This is a model prediction, not verified fact. Use as a support tool for human review.
              </div>
            </Card>

            {/* Text Highlights */}
            {result.highlights?.length > 0 && (
              <Card>
                <CardTitle icon={Sparkles}>Detected Patterns</CardTitle>
                <div className={styles.hlLegend}>
                  <span><span className={styles.dot} style={{ background: '#ef4444' }} />Sensational</span>
                  <span><span className={styles.dot} style={{ background: '#f59e0b' }} />Unverified Claim</span>
                  <span><span className={styles.dot} style={{ background: '#8b5cf6' }} />Excessive CAPS</span>
                </div>
                <HighlightedText text={result.article.text} highlights={result.highlights} />
              </Card>
            )}

            {/* Feature Importance */}
            <Card>
              <div className={styles.featureHeader}>
                <CardTitle icon={Zap}>Key Factors</CardTitle>
                <span className={styles.methodBadge}>
                  {result.explanation?.method === 'shap' ? 'SHAP' : 'Feature Weights'}
                </span>
              </div>
              <div className={styles.featureList}>
                {(result.explanation?.top_features || []).slice(0, 8).map((f, i) => (
                  <FeatureBar key={i} feature={f} />
                ))}
              </div>
            </Card>

            {/* Linguistic Profile */}
            <Card>
              <CardTitle icon={FileText}>Linguistic Profile</CardTitle>
              <div className={styles.metricsGrid}>
                {linguisticMetrics(result.linguistic_features, result.prediction).map((m, i) => (
                  <div key={i} className={styles.metricTile}>
                    <div className={styles.metricLabel}>{m.label}</div>
                    <div className={styles.metricValue} style={{ color: m.color || 'var(--text-primary)' }}>
                      {m.value}
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Feedback */}
            <Card>
              <CardTitle icon={MessageSquare}>Reviewer Feedback</CardTitle>
              {feedbackSent ? (
                <motion.div className={styles.feedbackSuccess}
                  initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
                  <CheckCircle size={16} /> Feedback recorded successfully
                </motion.div>
              ) : (
                <>
                  <p className={styles.feedbackDesc}>
                    Confirm, dismiss, or relabel this prediction to improve the model.
                  </p>
                  <div className={styles.fbActions}>
                    <button className={`${styles.fbBtn} ${styles.fbConfirm}`} onClick={() => handleFeedback('confirm')}>
                      ✓ Confirm
                    </button>
                    <button className={`${styles.fbBtn} ${styles.fbDismiss}`} onClick={() => handleFeedback('dismiss')}>
                      ✗ Dismiss
                    </button>
                    <button className={`${styles.fbBtn} ${styles.fbRelabel}`} onClick={() => setShowRelabel(v => !v)}>
                      ↺ Relabel
                    </button>
                  </div>
                  {showRelabel && (
                    <motion.div className={styles.relabelSection}
                      initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
                      <select className={styles.input} value={relabelVal} onChange={e => setRelabelVal(e.target.value)}>
                        <option value="REAL">REAL — Credible Content</option>
                        <option value="FAKE">FAKE — Misinformation</option>
                        <option value="UNCERTAIN">UNCERTAIN — Needs Review</option>
                      </select>
                      <textarea className={styles.textarea} rows={2}
                        placeholder="Optional reviewer note…"
                        value={note} onChange={e => setNote(e.target.value)} />
                      <button className={`${styles.fbBtn} ${styles.fbSubmit}`}
                        onClick={() => handleFeedback('relabel', relabelVal)}>
                        Submit Relabel
                      </button>
                    </motion.div>
                  )}
                </>
              )}
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

/* ── Sub-components ── */

function ProbBar({ label, value, color }) {
  return (
    <div className={styles.probBarRow}>
      <div className={styles.probBarLabel}>
        <span>{label}</span>
        <span style={{ color, fontFamily: 'var(--mono)', fontWeight: 600 }}>
          {(value * 100).toFixed(1)}%
        </span>
      </div>
      <div className={styles.probTrack}>
        <motion.div
          className={styles.probFill}
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${value * 100}%` }}
          transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
        />
      </div>
    </div>
  )
}

function FeatureBar({ feature: f }) {
  const impact = f.impact ?? f.shap_value ?? 0
  const isFake = f.impact_direction === 'fake' || impact > 0
  const pct = Math.min(Math.abs(impact) * 80, 100)
  const color = isFake ? 'var(--fake)' : 'var(--real)'
  return (
    <div className={styles.featureItem}>
      <div className={styles.featureRow}>
        <span className={styles.featureName}>{f.display_name || f.feature}</span>
        <span className={styles.featureTag} style={{ color, borderColor: color + '30', background: color + '10' }}>
          {isFake ? '→ Fake' : '→ Real'}
        </span>
      </div>
      <div className={styles.featureTrack}>
        <motion.div
          className={styles.featureFill}
          style={{ background: `linear-gradient(90deg, ${color}44, ${color})` }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
      {f.description && <div className={styles.featureDesc}>{f.description}</div>}
    </div>
  )
}

function HighlightedText({ text, highlights }) {
  if (!highlights?.length) return <p className={styles.hlText}>{text}</p>
  const sorted = [...highlights].sort((a, b) => a.start - b.start)
  const parts = []
  let last = 0
  for (const hl of sorted) {
    if (hl.start < last) continue
    if (hl.start > last) parts.push({ plain: text.slice(last, hl.start) })
    parts.push({ span: text.slice(hl.start, hl.end), color: hl.color, label: hl.label })
    last = hl.end
  }
  if (last < text.length) parts.push({ plain: text.slice(last) })
  return (
    <p className={styles.hlText}>
      {parts.map((p, i) => p.plain
        ? <span key={i}>{p.plain}</span>
        : <span key={i} className={styles.hlSpan}
            style={{ background: p.color + '22', color: p.color, borderBottom: `2px solid ${p.color}` }}
            title={p.label}>{p.span}</span>
      )}
    </p>
  )
}

function linguisticMetrics(f = {}, p = {}) {
  const cred = p.source_credibility_score ?? 0.5
  return [
    { label: 'Sentiment',       value: (f.vader_compound >= 0 ? '+' : '') + (f.vader_compound?.toFixed(3) ?? '—') },
    { label: 'Subjectivity',    value: `${((f.textblob_subjectivity || 0) * 100).toFixed(1)}%` },
    { label: 'Readability',     value: f.flesch_reading_ease?.toFixed(1) ?? '—' },
    { label: 'Word Count',      value: String(f.word_count ?? 0) },
    { label: 'Sensational',     value: `${((f.sensational_ratio || 0) * 100).toFixed(2)}%`, color: f.sensational_ratio > 0.05 ? 'var(--fake)' : 'var(--real)' },
    { label: 'CAPS Ratio',      value: `${((f.uppercase_ratio || 0) * 100).toFixed(1)}%`, color: f.uppercase_ratio > 0.1 ? 'var(--fake)' : 'var(--real)' },
    { label: 'Exclamations',    value: String(f.exclamation_count ?? 0), color: f.exclamation_count > 3 ? 'var(--fake)' : 'var(--text-primary)' },
    { label: 'Source Credibility', value: `${(cred * 100).toFixed(0)}%`, color: cred >= 0.6 ? 'var(--real)' : cred >= 0.4 ? 'var(--uncertain)' : 'var(--fake)' },
  ]
}
