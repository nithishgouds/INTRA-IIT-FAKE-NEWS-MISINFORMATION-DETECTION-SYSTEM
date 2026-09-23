import { motion } from 'framer-motion'
import styles from './Card.module.css'

export default function Card({ children, className = '', glow = false, ...props }) {
  return (
    <motion.div
      className={`${styles.card} ${glow ? styles.glow : ''} ${className}`}
      whileHover={{ borderColor: 'rgba(255,255,255,0.12)' }}
      transition={{ duration: 0.15 }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

export function CardTitle({ children, icon: Icon }) {
  return (
    <div className={styles.title}>
      {Icon && <span className={styles.titleIcon}><Icon size={17} /></span>}
      {children}
    </div>
  )
}
