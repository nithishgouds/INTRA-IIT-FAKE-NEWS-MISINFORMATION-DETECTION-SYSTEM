import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  Search, Zap, AlertTriangle, CheckCircle, HelpCircle,
  MessageSquare, ChevronRight, Sparkles, FileText, Globe, ShieldCheck, ShieldAlert
} from 'lucide-react'
import Card, { CardTitle } from '../components/Card'
import { analyzeArticle, submitFeedback } from '../api/client'
import styles from './AnalyzePage.module.css'

const SAMPLES = {
  real: {
    title: 'ISRO Successfully Launches GSLV-F17 Mission',
    text: `The Indian Space Research Organisation (ISRO) successfully launched the GSLV-F17 launch vehicle on Tuesday morning from the Satish Dhawan Space Centre in Sriharikota. The mission successfully deployed advanced meteorology and earth observation satellites into geostationary orbit. Mission Director Dr. K. Raman announced that all payload telemetry parameters are normal and within expected operational limits.`,
    source: 'Indian Space Research Organisation (ISRO)',
    author: 'ISRO Media Centre',
    url: 'https://www.isro.gov.in/',
  },
  fake: {
    title: 'SHOCKING BOMBSHELL: Gov Hiding Secret Cure!!!',
    text: `BREAKING!!! You won't BELIEVE what Big Pharma has been hiding for DECADES!!! SECRET documents EXPOSED show that the government has been SUPPRESSING a natural cure that DESTROYS all disease!!! They are TERRIFIED because this information will BANKRUPT the entire medical industry!!! SHARE THIS IMMEDIATELY before it gets CENSORED!!! The mainstream media REFUSES to cover this BOMBSHELL story because they are all CONTROLLED by the deep state!!!! Wake up people!!! Your health is at stake!!!`,
    source: 'infowars.com',
    author: 'Anonymous',
    url: 'https://infowars.com/secret-cure',
  },
  adv_fake: {
    title: 'Astronomical Observatory Reports Rare Moon Phase Phenomenon',
    text: `Researchers at an international astronomical observatory have confirmed that Earth's Moon will temporarily disappear from the night sky for approximately 72 hours beginning next week. According to researchers, the phenomenon is caused by a rare gravitational interaction between the Earth, Moon and Sun. Citizens are advised to remain indoors during this period.`,
    source: 'Independent Astronomy Blog',
    author: 'Staff Correspondent',
    url: 'https://astronomy-unverified-blog.org/moon-disappears',
  },
  adv_real: {
    title: 'BREAKING: ISRO GSLV-F17 HISTORIC LAUNCH SUCCESS!!!',
    text: `BREAKING NEWS: In an incredible achievement for India, ISRO has successfully launched the GSLV-F17 satellite vehicle into geostationary orbit from Sriharikota! The satellite payload was injected with high precision, marking a major milestone for national space exploration!`,
    source: 'Indian Space Research Organisation (ISRO)',
    author: 'Press Bureau',
    url: 'https://www.isro.gov.in/',
  }
}

const VERDICT_CONFIG = {
  FAKE: {
    icon: AlertTriangle,
    label: 'Likely Misinformation',
    sublabel: 'Statistical and linguistic patterns strongly match known misinformation datasets',
    color: 'var(--fake)',
    bg: 'var(--fake-bg)',
    border: 'var(--fake-border)',
  },
  REAL: {
    icon: CheckCircle,
    label: 'Likely Credible',
    sublabel: 'Linguistic markers and source patterns align with credible journalistic standards',
    color: 'var(--real)',
    bg: 'var(--real-bg)',
    border: 'var(--real-border)',
  },
  UNCERTAIN: {
    icon: HelpCircle,
    label: 'Uncertain / Ambiguous',
    sublabel: 'Mixed signals detected — recommended for prioritized human verification',
    color: 'var(--uncertain)',
    bg: 'var(--uncertain-bg)',
    border: 'var(--uncertain-border)',
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
    setForm({ ...SAMPLES[type] })
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

  // Collect unique active highlight types
  const activeHighlightTypes = result?.highlights ? [...new Set(result.highlights.map(h => h.type))] : []

  return (
    <div className={styles.layout}>
      {/* ─── Input Panel ─── */}
      <Card className={styles.inputCard} glow>
        <CardTitle icon={Search}>Submit Content for Analysis</CardTitle>

        {/* Sample buttons */}
        <div className={styles.sampleRow}>
          <span className={styles.sampleLabel}>Try presets:</span>
          <button className={`${styles.sampleBtn} ${styles.sampleReal}`} onClick={() => loadSample('real')}>
            <CheckCircle size={12} /> Real News (ISRO)
          </button>
          <button className={`${styles.sampleBtn} ${styles.sampleFake}`} onClick={() => loadSample('fake')}>
            <AlertTriangle size={12} /> Clickbait Fake
          </button>
          <button className={`${styles.sampleBtn} ${styles.sampleAdv}`} onClick={() => loadSample('adv_fake')}>
            <Zap size={12} /> Calm Fake (Moon)
          </button>
          <button className={`${styles.sampleBtn} ${styles.sampleAdv}`} onClick={() => loadSample('adv_real')}>
            <Sparkles size={12} /> Excited Real
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
              rows={8}
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
              <input className={styles.input} placeholder="e.g. Indian Space Research Organisation (ISRO)"
                value={form.source} onChange={e => setForm(f => ({ ...f, source: e.target.value }))} />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>Author</label>
              <input className={styles.input} placeholder="e.g. Jane Smith"
                value={form.author} onChange={e => setForm(f => ({ ...f, author: e.target.value }))} />
            </div>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Source URL <span className={styles.optional}>(used for domain reputation lookup)</span></label>
            <input className={styles.input} type="url" placeholder="https://www.isro.gov.in/..."
              value={form.url} onChange={e => setForm(f => ({ ...f, url: e.target.value }))} />
          </div>

          <motion.button
            className={styles.analyzeBtn}
            type="submit"
            disabled={loading}
            whileTap={{ scale: 0.98 }}
          >
            {loading
              ? <><span className={styles.spinner} /> Analyzing Model & Source Signals…</>
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
                    Content Veracity: {verdict.label}
                  </div>
                  <div className={styles.verdictSub}>
                    Source-Independent Text Classification: {verdict.sublabel}
                  </div>
                </div>
                <div className={styles.confBadge}>
                  <span className={styles.confVal} style={{ color: verdict.color }}>
                    {(result.prediction.confidence * 100).toFixed(1)}%
                  </span>
                  <span className={styles.confLabel}>Model Probability</span>
                </div>
              </div>

              {/* Probability Bars */}
              <div className={styles.probBars}>
                <ProbBar label="🟢 Credibility Probability" value={result.prediction.real_probability} color="var(--real)" />
                <ProbBar label="🔴 Misinformation Probability" value={result.prediction.fake_probability} color="var(--fake)" />
              </div>

              <div className={styles.disclaimer}>
                ⚠️ <strong>Independent Signals Architecture:</strong> Content veracity reflects textual and linguistic pattern analysis independent of publisher domain reputation. A verified source does not automatically validate false claims.
              </div>
            </Card>

            {/* Source & Domain Credibility Breakdown */}
            {result.source_evaluation && (
              <Card>
                <CardTitle icon={Globe}>Source & Domain Reputation</CardTitle>
                
                {/* Publisher-Domain Mismatch Alert */}
                {result.source_evaluation.is_mismatch && (
                  <div className={styles.mismatchAlert}>
                    <AlertTriangle size={18} className={styles.mismatchIcon} />
                    <div>
                      <strong>Publisher-Domain Mismatch Detected:</strong>
                      <span>{result.source_evaluation.mismatch_warning || `Claimed publisher does not match URL domain '${result.source_evaluation.domain}'.`}</span>
                    </div>
                  </div>
                )}

                <div className={styles.sourceEvalCard}>
                  <div className={styles.sourceTopRow}>
                    <span className={styles.sourceName}>
                      {result.source_evaluation.claimed_publisher || result.source_evaluation.source_name || 'Publisher Unspecified'}
                    </span>
                    <span className={styles.sourceTier} style={{
                      borderColor: result.source_evaluation.is_mismatch ? 'var(--fake)' : result.source_evaluation.credibility_score >= 0.85 ? 'var(--real)' : result.source_evaluation.credibility_score <= 0.3 ? 'var(--fake)' : 'var(--uncertain)',
                      color: result.source_evaluation.is_mismatch ? 'var(--fake)' : result.source_evaluation.credibility_score >= 0.85 ? 'var(--real)' : result.source_evaluation.credibility_score <= 0.3 ? 'var(--fake)' : 'var(--uncertain)',
                    }}>
                      {result.source_evaluation.tier}
                    </span>
                  </div>

                  <div className={styles.sourceScoreRow}>
                    <span className={styles.sourceScoreLabel}>
                      Verified Origin Domain: <code style={{ fontFamily: 'var(--mono)', color: 'var(--text-secondary)' }}>{result.source_evaluation.domain}</code>
                    </span>
                    <span className={styles.sourceScoreVal} style={{
                      color: result.source_evaluation.is_mismatch ? 'var(--fake)' : result.source_evaluation.credibility_score >= 0.85 ? 'var(--real)' : result.source_evaluation.credibility_score <= 0.3 ? 'var(--fake)' : 'var(--uncertain)',
                    }}>
                      {(result.source_evaluation.credibility_score * 100).toFixed(0)}% Source Authority
                    </span>
                  </div>

                  <div className={styles.sourceDesc}>
                    {result.source_evaluation.explanation}
                  </div>
                  <div className={styles.sourceNotice}>
                    * Note: Source reputation measures institutional standing of the origin domain and is evaluated independently from textual veracity.
                  </div>
                </div>
              </Card>
            )}

            {/* Detected Linguistic Patterns */}
            <Card>
              <CardTitle icon={Sparkles}>Detected Text Patterns</CardTitle>
              
              {result.highlights?.length === 0 ? (
                <div className={styles.noHlNotice}>
                  <CheckCircle size={14} /> No suspicious linguistic markers detected (no sensational clickbait vocabulary, speculative hedges, or excessive capitalization).
                </div>
              ) : (
                <div className={styles.hlLegend}>
                  {activeHighlightTypes.includes('sensational') && (
                    <span><span className={styles.dot} style={{ background: '#ef4444' }} />Sensational Language ({result.highlights.filter(h => h.type === 'sensational').length})</span>
                  )}
                  {activeHighlightTypes.includes('hedge') && (
                    <span><span className={styles.dot} style={{ background: '#f59e0b' }} />Unverified Claim Indicator ({result.highlights.filter(h => h.type === 'hedge').length})</span>
                  )}
                  {activeHighlightTypes.includes('caps') && (
                    <span><span className={styles.dot} style={{ background: '#8b5cf6' }} />Excessive Capitalization ({result.highlights.filter(h => h.type === 'caps').length})</span>
                  )}
                </div>
              )}

              <HighlightedText text={result.article.analyzed_text || result.article.text} highlights={result.highlights} />
            </Card>

            {/* Feature Importance (SHAP) */}
            <Card>
              <div className={styles.featureHeader}>
                <CardTitle icon={Zap}>Model Feature Contributions (XAI)</CardTitle>
                <span className={styles.methodBadge}>
                  {result.explanation?.method === 'shap' ? 'SHAP Values' : 'Feature Weights'}
                </span>
              </div>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
                Shows how individual linguistic and metadata signals numerically pushed the prediction towards <strong>Credible (+)</strong> or <strong>Misinformation (-)</strong>.
              </p>
              <div className={styles.featureList}>
                {(result.explanation?.top_features || []).slice(0, 8).map((f, i) => (
                  <FeatureBar key={i} feature={f} />
                ))}
              </div>
            </Card>

            {/* Linguistic Profile */}
            <Card>
              <CardTitle icon={FileText}>Linguistic Signals Summary</CardTitle>
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

            {/* Reviewer Feedback Loop */}
            <Card>
              <CardTitle icon={MessageSquare}>Human-in-the-Loop Review</CardTitle>
              {feedbackSent ? (
                <motion.div className={styles.feedbackSuccess}
                  initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
                  <CheckCircle size={16} /> Decision recorded to reviewer queue. Model update queued.
                </motion.div>
              ) : (
                <>
                  <p className={styles.feedbackDesc}>
                    Confirm, dismiss, or relabel this automated prediction to maintain trust accuracy and update the model training pipeline.
                  </p>
                  <div className={styles.fbActions}>
                    <button className={`${styles.fbBtn} ${styles.fbConfirm}`} onClick={() => handleFeedback('confirm')}>
                      ✓ Confirm Prediction
                    </button>
                    <button className={`${styles.fbBtn} ${styles.fbDismiss}`} onClick={() => handleFeedback('dismiss')}>
                      ✗ Dismiss Flag
                    </button>
                    <button className={`${styles.fbBtn} ${styles.fbRelabel}`} onClick={() => setShowRelabel(v => !v)}>
                      ↺ Relabel Article
                    </button>
                  </div>
                  {showRelabel && (
                    <motion.div className={styles.relabelSection}
                      initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
                      <select className={styles.input} value={relabelVal} onChange={e => setRelabelVal(e.target.value)}>
                        <option value="REAL">REAL — Verified Credible Content</option>
                        <option value="FAKE">FAKE — Confirmed Misinformation</option>
                        <option value="UNCERTAIN">UNCERTAIN — Needs Fact-Check Investigation</option>
                      </select>
                      <textarea className={styles.textarea} rows={2}
                        placeholder="Optional fact-checker or reviewer notes…"
                        value={note} onChange={e => setNote(e.target.value)} />
                      <button className={`${styles.fbBtn} ${styles.fbSubmit}`}
                        onClick={() => handleFeedback('relabel', relabelVal)}>
                        Submit Relabel Decision
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
  const pct = Math.max(0, Math.min(100, (value || 0) * 100))
  return (
    <div className={styles.probBarRow}>
      <div className={styles.probBarLabel}>
        <span>{label}</span>
        <span style={{ color, fontFamily: 'var(--mono)', fontWeight: 700 }}>
          {pct.toFixed(1)}%
        </span>
      </div>
      <div className={styles.probTrack}>
        <motion.div
          className={styles.probFill}
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
        />
      </div>
    </div>
  )
}

function FeatureBar({ feature: f }) {
  const rawImpact = f.impact ?? f.shap_value ?? 0
  const isFake = f.impact_direction === 'fake' || rawImpact > 0
  const absVal = Math.abs(rawImpact)
  const pct = Math.min(Math.max(absVal * 70, 8), 100)
  const color = isFake ? 'var(--fake)' : 'var(--real)'
  const tagText = isFake
    ? `+${absVal.toFixed(2)} toward Misinformation`
    : `+${absVal.toFixed(2)} toward Credible`

  return (
    <div className={styles.featureItem}>
      <div className={styles.featureRow}>
        <span className={styles.featureName}>{f.display_name || f.feature}</span>
        <span className={styles.featureContribution} style={{ color }}>
          {tagText}
        </span>
      </div>
      <div className={styles.featureTrack}>
        <motion.div
          className={styles.featureFill}
          style={{ background: `linear-gradient(90deg, ${color}33, ${color})` }}
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
    { label: 'Sentiment Index',    value: (f.vader_compound >= 0 ? '+' : '') + (f.vader_compound?.toFixed(3) ?? '0.000') },
    { label: 'Subjectivity',       value: `${((f.textblob_subjectivity || 0) * 100).toFixed(1)}%` },
    { label: 'Readability Ease',   value: f.flesch_reading_ease?.toFixed(1) ?? '—' },
    { label: 'Word Count',         value: String(f.word_count ?? 0) },
    { label: 'Sensational Ratio',  value: `${((f.sensational_ratio || 0) * 100).toFixed(2)}%`, color: f.sensational_ratio > 0.05 ? 'var(--fake)' : 'var(--real)' },
    { label: 'CAPS Ratio',         value: `${((f.uppercase_ratio || 0) * 100).toFixed(1)}%`, color: f.uppercase_ratio > 0.1 ? 'var(--fake)' : 'var(--real)' },
    { label: 'Exclamations',       value: String(f.exclamation_count ?? 0), color: f.exclamation_count > 2 ? 'var(--fake)' : 'var(--text-primary)' },
    { label: 'Source Authority',   value: `${(cred * 100).toFixed(0)}%`, color: cred >= 0.8 ? 'var(--real)' : cred >= 0.4 ? 'var(--uncertain)' : 'var(--fake)' },
  ]
}
