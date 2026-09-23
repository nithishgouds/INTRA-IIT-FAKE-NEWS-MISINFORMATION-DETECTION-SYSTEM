import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Shield, Search, Globe, CheckCircle, AlertTriangle, HelpCircle } from 'lucide-react'
import Card, { CardTitle } from '../components/Card'
import { getSources } from '../api/client'
import styles from './SourcesPage.module.css'

export default function SourcesPage() {
  const [sources, setSources] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const res = await getSources()
        setSources(res.data || [])
      } catch {
        // fallback
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const filtered = sources.filter(s =>
    s.source_name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className={styles.container}>
      <div className={styles.searchBar}>
        <Search size={18} style={{ color: 'var(--text-muted)' }} />
        <input
          type="text"
          className={styles.searchInput}
          placeholder="Filter by domain or publisher name (e.g. reuters, bbc, infowars)..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <Card glow>
        <CardTitle icon={Shield}>Publisher Reliability Database & Credibility Ratings</CardTitle>
        <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginBottom: 20 }}>
          Domain credibility scores are updated based on historical domain reputation and empirical confirmation ratios. Low credibility scores directly influence the multimodal classifier’s risk assessment.
        </p>

        {loading ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 24 }}>Loading source profiles...</p>
        ) : filtered.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 24 }}>No matching sources found.</p>
        ) : (
          <div className={styles.sourcesGrid}>
            {filtered.map((s) => {
              const scorePct = Math.round(s.credibility_score * 100)
              const isHigh = scorePct >= 65
              const isLow = scorePct <= 35
              const barColor = isHigh ? 'var(--real)' : isLow ? 'var(--fake)' : 'var(--uncertain)'
              const label = isHigh ? 'High Credibility' : isLow ? 'High Misinformation Risk' : 'Mixed / Neutral'

              return (
                <motion.div
                  key={s.source_name}
                  className={styles.sourceCard}
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                >
                  <div className={styles.sourceHeader}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Globe size={16} style={{ color: 'var(--primary-light)' }} />
                      <span className={styles.domainName}>{s.source_name}</span>
                    </div>
                    {isHigh ? (
                      <CheckCircle size={16} style={{ color: 'var(--real)' }} />
                    ) : isLow ? (
                      <AlertTriangle size={16} style={{ color: 'var(--fake)' }} />
                    ) : (
                      <HelpCircle size={16} style={{ color: 'var(--uncertain)' }} />
                    )}
                  </div>

                  <div className={styles.meterContainer}>
                    <div className={styles.meterHeader}>
                      <span>{label}</span>
                      <span style={{ fontWeight: 700, color: barColor }}>{scorePct}%</span>
                    </div>
                    <div className={styles.meterTrack}>
                      <div
                        className={styles.meterFill}
                        style={{ width: `${scorePct}%`, background: barColor }}
                      />
                    </div>
                  </div>

                  <div className={styles.statsRow}>
                    <span>Articles Evaluated: <strong>{s.total_articles}</strong></span>
                    <span>Fake: <strong style={{ color: 'var(--fake)' }}>{s.fake_count}</strong></span>
                    <span>Real: <strong style={{ color: 'var(--real)' }}>{s.real_count}</strong></span>
                  </div>
                </motion.div>
              )
            })}
          </div>
        )}
      </Card>
    </div>
  )
}
