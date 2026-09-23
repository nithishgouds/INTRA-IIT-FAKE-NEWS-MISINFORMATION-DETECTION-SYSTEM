import { useState, useEffect } from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, LayoutDashboard, FileText, Shield, BarChart2,
  RefreshCw, Menu, X, Zap, Activity
} from 'lucide-react'
import toast from 'react-hot-toast'
import { getHealth, triggerTrain } from '../api/client'
import styles from './Layout.module.css'

const NAV = [
  { to: '/analyze',   icon: Search,          label: 'Analyze',        desc: 'Submit content' },
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard',      desc: 'Review queue' },
  { to: '/batch',     icon: FileText,        label: 'Batch Analysis', desc: 'Bulk processing' },
  { to: '/sources',   icon: Shield,          label: 'Sources',        desc: 'Credibility' },
  { to: '/metrics',   icon: BarChart2,       label: 'Metrics',        desc: 'Model eval' },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [health, setHealth] = useState(null)
  const [training, setTraining] = useState(false)
  const location = useLocation()

  useEffect(() => {
    checkHealth()
    const id = setInterval(checkHealth, 30000)
    return () => clearInterval(id)
  }, [])

  // Close sidebar on mobile when route changes
  useEffect(() => {
    if (window.innerWidth < 900) setSidebarOpen(false)
  }, [location.pathname])

  async function checkHealth() {
    try {
      const { data } = await getHealth()
      setHealth({ ok: true, version: data.model_version })
    } catch {
      setHealth({ ok: false })
    }
  }

  async function handleRetrain() {
    setTraining(true)
    const tid = toast.loading('Retraining model on latest data...')
    try {
      const { data } = await triggerTrain()
      toast.success(
        `Model retrained! Acc: ${(data.metrics?.accuracy * 100).toFixed(1)}%  F1: ${(data.metrics?.f1_score * 100).toFixed(1)}%`,
        { id: tid, duration: 5000 }
      )
      checkHealth()
    } catch (e) {
      toast.error(`Training failed: ${e.response?.data?.detail || e.message}`, { id: tid })
    } finally {
      setTraining(false)
    }
  }

  const pageTitles = {
    '/analyze':   ['Content Analysis',    'Submit article text to detect misinformation'],
    '/dashboard': ['Review Dashboard',    'Prioritized queue of flagged content'],
    '/batch':     ['Batch Analysis',      'Process multiple articles at once'],
    '/sources':   ['Source Credibility',  'Publisher reliability profiles'],
    '/metrics':   ['Model Evaluation',    'Classification metrics and failure analysis'],
  }
  const [title, subtitle] = pageTitles[location.pathname] || ['TruthLens', '']

  return (
    <div className={styles.shell}>
      {/* ── Sidebar ── */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            className={styles.sidebar}
            initial={{ x: -260 }}
            animate={{ x: 0 }}
            exit={{ x: -260 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            {/* Logo */}
            <div className={styles.logo}>
              <div className={styles.logoIcon}>
                <Zap size={18} strokeWidth={2.5} />
              </div>
              <div>
                <div className={styles.logoName}>TruthLens</div>
                <div className={styles.logoSub}>AI Detection</div>
              </div>
            </div>

            {/* Nav */}
            <nav className={styles.nav}>
              {NAV.map(({ to, icon: Icon, label, desc }) => (
                <NavLink key={to} to={to} className={({ isActive }) =>
                  `${styles.navItem} ${isActive ? styles.navActive : ''}`
                }>
                  <div className={styles.navIcon}><Icon size={17} /></div>
                  <div className={styles.navText}>
                    <span className={styles.navLabel}>{label}</span>
                    <span className={styles.navDesc}>{desc}</span>
                  </div>
                </NavLink>
              ))}
            </nav>

            {/* Footer badge */}
            <div className={styles.sidebarFooter}>
              <div className={styles.hackBadge}>
                <Activity size={13} />
                <div>
                  <div className={styles.hackTitle}>Intra-IIT 2026</div>
                  <div className={styles.hackTrack}>NLP · Trust & Safety</div>
                </div>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* ── Sidebar Overlay (mobile) ── */}
      {sidebarOpen && (
        <div className={styles.overlay} onClick={() => setSidebarOpen(false)} />
      )}

      {/* ── Main ── */}
      <div className={`${styles.main} ${sidebarOpen ? styles.mainShifted : ''}`}>
        {/* Header */}
        <header className={styles.header}>
          <div className={styles.headerLeft}>
            <button className={styles.menuBtn} onClick={() => setSidebarOpen(v => !v)}>
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <div>
              <h1 className={styles.pageTitle}>{title}</h1>
              <p className={styles.pageSub}>{subtitle}</p>
            </div>
          </div>
          <div className={styles.headerRight}>
            {/* Health pill */}
            <div className={`${styles.healthPill} ${health?.ok ? styles.healthOk : styles.healthErr}`}>
              <span className={styles.healthDot} />
              <span>{health?.ok ? `Model ${health.version || 'v1.0'}` : 'Offline'}</span>
            </div>
            {/* Retrain */}
            <button className={styles.retrainBtn} onClick={handleRetrain} disabled={training}>
              <RefreshCw size={15} className={training ? styles.spin : ''} />
              <span>{training ? 'Training…' : 'Retrain'}</span>
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className={styles.content}>
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.18, ease: 'easeOut' }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}
