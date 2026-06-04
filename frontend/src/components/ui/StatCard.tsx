import { motion } from 'framer-motion'
import type { LucideIcon } from 'lucide-react'

interface StatCardProps {
  label: string
  value: string
  change?: string
  positive?: boolean
  icon: LucideIcon
  index?: number
}

export function StatCard({ label, value, change, positive, icon: Icon, index = 0 }: StatCardProps) {
  return (
    <motion.div
      className="glass-card-hover rounded-[20px] p-4 sm:rounded-[24px] sm:p-6"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.08, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-app-muted">{label}</p>
          <p className="mt-2 text-2xl font-semibold tracking-tight text-black sm:text-3xl">{value}</p>
          {change && (
            <p className={`mt-1 text-xs ${positive ? 'text-emerald-600' : 'text-red-600'}`}>
              {change}
            </p>
          )}
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-black/[0.04]">
          <Icon className="h-5 w-5 text-app-subtle" />
        </div>
      </div>
    </motion.div>
  )
}
