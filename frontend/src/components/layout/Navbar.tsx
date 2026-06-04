import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '../ui/Button'
import { Menu, X } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'

const navLinks = [
  { label: 'Features', href: '/#features' },
  { label: 'Platform', href: '/#platform' },
  { label: 'How it works', href: '/#how-it-works' },
]

export function Navbar() {
  const location = useLocation()
  const { isAuthenticated } = useAuth()
  const isAuth = location.pathname === '/login' || location.pathname === '/register'
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="fixed top-0 z-50 w-full px-4 pt-4 md:px-6">
      <motion.header
        initial={{ y: -24, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="glass-nav mx-auto flex max-w-5xl items-center justify-between rounded-full px-3 py-2 md:px-4 md:py-2.5"
      >
        <Link to="/" className="flex items-center gap-2.5 pl-2 md:pl-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-black">
            <span className="text-xs font-bold text-white">P</span>
          </div>
          <span className="text-[15px] font-semibold tracking-tight text-black">PropIQ</span>
        </Link>

        {!isAuth && (
          <nav className="hidden items-center gap-1 md:flex">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="rounded-full px-4 py-2 text-[13px] font-medium text-app-muted transition-all hover:bg-black/[0.04] hover:text-black"
              >
                {link.label}
              </a>
            ))}
          </nav>
        )}

        <div className="hidden items-center gap-2 md:flex">
          {isAuthenticated ? (
            <Button variant="primary" size="sm" to="/dashboard">
              Dashboard
            </Button>
          ) : (
            <>
              <Button variant="ghost" size="sm" to="/login">
                Log in
              </Button>
              <Button variant="primary" size="sm" to="/login">
                Get started
              </Button>
            </>
          )}
        </div>

        <button
          type="button"
          className="rounded-full p-2 text-app-muted hover:bg-black/[0.04] md:hidden"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </motion.header>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            className="glass-nav mx-auto mt-2 max-w-5xl overflow-hidden rounded-3xl p-4 md:hidden"
          >
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="block rounded-xl px-4 py-3 text-sm font-medium text-app-subtle hover:bg-black/[0.04]"
                onClick={() => setMobileOpen(false)}
              >
                {link.label}
              </a>
            ))}
            <div className="mt-3 flex flex-col gap-2 border-t border-black/[0.06] pt-3">
              <Button variant="ghost" size="sm" to="/login">
                Log in
              </Button>
              <Button variant="primary" size="sm" to="/login">
                Get started
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
