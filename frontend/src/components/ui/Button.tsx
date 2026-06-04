import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'outline' | 'white'
type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  to?: string
  children: ReactNode
}

const variants: Record<ButtonVariant, string> = {
  primary: 'bg-black text-white hover:bg-neutral-800 border border-transparent shadow-sm',
  white: 'bg-white text-black hover:bg-neutral-100 border border-white/20 shadow-lg',
  secondary: 'bg-app-muted-bg text-black hover:bg-neutral-200 border border-black/[0.06]',
  ghost: 'bg-transparent text-app-muted hover:text-black hover:bg-black/[0.04] border border-transparent',
  outline: 'bg-transparent text-black hover:bg-black/[0.04] border border-black/10 hover:border-black/20',
}

const sizes: Record<ButtonSize, string> = {
  sm: 'h-9 px-4 text-[13px] rounded-full',
  md: 'h-10 px-5 text-sm rounded-full',
  lg: 'h-12 px-7 text-sm rounded-full',
}

const motionProps = { whileHover: { scale: 1.02 }, whileTap: { scale: 0.98 } }

export function Button({
  variant = 'primary',
  size = 'md',
  to,
  className = '',
  children,
  type = 'button',
  ...props
}: ButtonProps) {
  const classes = `inline-flex items-center justify-center gap-2 font-medium transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none ${variants[variant]} ${sizes[size]} ${className}`

  if (to) {
    return (
      <motion.span {...motionProps} className="inline-flex">
        <Link to={to} className={classes}>
          {children}
        </Link>
      </motion.span>
    )
  }

  return (
    <motion.span {...motionProps} className={`inline-flex ${className.includes('w-full') ? 'w-full' : ''}`}>
      <button type={type} className={`${classes} ${className.includes('w-full') ? 'w-full' : ''}`} {...props}>
        {children}
      </button>
    </motion.span>
  )
}
