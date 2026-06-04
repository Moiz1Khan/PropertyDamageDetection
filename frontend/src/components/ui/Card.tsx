import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  hover?: boolean
  padding?: 'sm' | 'md' | 'lg' | 'none'
  animate?: boolean
}

const paddingMap = { none: '', sm: 'p-4', md: 'p-6', lg: 'p-8' }

export function Card({ children, className = '', hover = false, padding = 'md', animate = false }: CardProps) {
  const base = `${hover ? 'glass-card-hover' : 'glass-card'} rounded-[24px] ${paddingMap[padding]} ${className}`

  if (animate || hover) {
    return (
      <motion.div
        className={base}
        whileHover={hover ? { y: -4, transition: { duration: 0.3 } } : undefined}
        initial={animate ? { opacity: 0, y: 20 } : undefined}
        whileInView={animate ? { opacity: 1, y: 0 } : undefined}
        viewport={animate ? { once: true, margin: '-40px' } : undefined}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      >
        {children}
      </motion.div>
    )
  }

  return <div className={base}>{children}</div>
}
