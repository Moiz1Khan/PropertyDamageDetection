type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info'

const variants: Record<BadgeVariant, string> = {
  default: 'bg-black/[0.05] text-app-subtle border-black/[0.06]',
  success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  warning: 'bg-amber-50 text-amber-700 border-amber-200',
  danger: 'bg-red-50 text-red-700 border-red-200',
  info: 'bg-blue-50 text-blue-700 border-blue-200',
}

export function Badge({
  children,
  variant = 'default',
  className = '',
}: {
  children: React.ReactNode
  variant?: BadgeVariant
  className?: string
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${variants[variant]} ${className}`}
    >
      {children}
    </span>
  )
}

export function StatusBadge({ status }: { status: 'analyzing' | 'complete' | 'draft' | 'Active' | 'Pending' }) {
  const map = {
    analyzing: { variant: 'info' as const, label: 'Analyzing' },
    complete: { variant: 'success' as const, label: 'Complete' },
    draft: { variant: 'default' as const, label: 'Draft' },
    Active: { variant: 'success' as const, label: 'Active' },
    Pending: { variant: 'warning' as const, label: 'Pending' },
  }
  const { variant, label } = map[status]
  return <Badge variant={variant}>{label}</Badge>
}
