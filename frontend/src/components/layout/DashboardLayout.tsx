import { NavLink, Outlet, Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  Building2,
  GitCompare,
  Trophy,
  FileText,
  Settings,
  Users,
  Plus,
  LogOut,
  Menu,
  X,
} from 'lucide-react'
import { useState } from 'react'
import { useAuth, roleLabel } from '../../context/AuthContext'
import { Badge } from '../ui/Badge'
import { PageTransition } from '../motion/FadeIn'

const mainNav = [
  { to: '/dashboard', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/dashboard/properties', label: 'Properties', icon: Building2 },
  { to: '/dashboard/compare', label: 'Compare Deals', icon: GitCompare },
  { to: '/dashboard/rankings', label: 'Rankings', icon: Trophy },
  { to: '/dashboard/reports', label: 'Reports', icon: FileText },
]

const adminNav = [
  { to: '/admin/users', label: 'Users', icon: Users },
  { to: '/admin/settings', label: 'Settings', icon: Settings },
]

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const isAdmin = user?.role === 'admin'

  const handleLogout = () => {
    logout()
    onNavigate?.()
    navigate('/login')
  }

  return (
    <>
      <div className="flex h-16 items-center gap-2 border-b border-black/[0.06] px-6">
        <Link to="/" className="flex items-center gap-2" onClick={onNavigate}>
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-black">
            <span className="text-[10px] font-bold text-white sm:text-xs">O</span>
          </div>
          <span className="truncate font-semibold tracking-tight text-black">OffmarketStream</span>
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <Link
          to="/dashboard/properties/new"
          onClick={onNavigate}
          className="mb-6 flex w-full items-center justify-center gap-2 rounded-full bg-black py-2.5 text-sm font-medium text-white transition-all hover:bg-neutral-800"
        >
          <Plus className="h-4 w-4" />
          New Analysis
        </Link>

        <p className="mb-2 px-3 text-xs font-medium uppercase tracking-wider text-app-muted">Main</p>
        <nav className="space-y-1">
          {mainNav.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onNavigate}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm transition-all ${
                  isActive
                    ? 'bg-black/[0.06] font-medium text-black'
                    : 'text-app-muted hover:bg-black/[0.04] hover:text-black'
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        {isAdmin && (
          <>
            <p className="mb-2 mt-8 px-3 text-xs font-medium uppercase tracking-wider text-app-muted">
              Admin
            </p>
            <nav className="space-y-1">
              {adminNav.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  onClick={onNavigate}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm transition-all ${
                      isActive
                        ? 'bg-black/[0.06] font-medium text-black'
                        : 'text-app-muted hover:bg-black/[0.04] hover:text-black'
                    }`
                  }
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </NavLink>
              ))}
            </nav>
          </>
        )}
      </div>

      <div className="border-t border-black/[0.06] p-4">
        {user && (
          <div className="flex items-center gap-3 rounded-2xl px-3 py-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-black text-sm font-medium text-white">
              {user.name.charAt(0)}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-black">{user.name}</p>
              <p className="truncate text-xs text-app-muted">{user.email}</p>
            </div>
          </div>
        )}
        {user && <Badge className="mx-3 mt-1">{roleLabel(user.role)}</Badge>}
        <button
          type="button"
          onClick={handleLogout}
          className="mt-3 flex w-full items-center gap-2 rounded-2xl px-3 py-2 text-sm text-app-muted transition-colors hover:bg-black/[0.04] hover:text-black"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </>
  )
}

export function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const { user } = useAuth()

  return (
    <div className="flex min-h-screen bg-app-bg">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col border-r border-black/[0.06] bg-white lg:flex">
        <SidebarContent />
      </aside>

      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm lg:hidden"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', damping: 28, stiffness: 300 }}
              className="fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-white shadow-xl lg:hidden"
            >
              <button
                type="button"
                className="absolute right-4 top-4 text-app-muted"
                onClick={() => setMobileOpen(false)}
              >
                <X className="h-5 w-5" />
              </button>
              <SidebarContent onNavigate={() => setMobileOpen(false)} />
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      <div className="flex flex-1 flex-col lg:pl-64">
        <header className="sticky top-0 z-30 flex h-14 min-h-14 items-center gap-3 border-b border-black/[0.06] bg-app-bg/90 px-4 backdrop-blur-xl sm:h-16 sm:gap-4 sm:px-6">
          <button type="button" className="text-app-muted lg:hidden" onClick={() => setMobileOpen(true)}>
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex-1" />
          {user && (
            <p className="hidden text-sm text-app-muted sm:block">
              Welcome, <span className="font-medium text-black">{user.name.split(' ')[0]}</span>
            </p>
          )}
          <Link
            to="/dashboard/properties/new"
            className="flex items-center gap-2 rounded-full bg-black px-4 py-2 text-sm font-medium text-white lg:hidden"
          >
            <Plus className="h-4 w-4" />
            New
          </Link>
        </header>

        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <PageTransition>
            <Outlet />
          </PageTransition>
        </main>
      </div>
    </div>
  )
}
