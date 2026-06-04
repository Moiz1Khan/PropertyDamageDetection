import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Card } from '../components/ui/Card'
import { useAuth, DEMO_ACCOUNTS, roleLabel } from '../context/AuthContext'
import { Copy, CheckCircle2, AlertCircle } from 'lucide-react'

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  const [email, setEmail] = useState('demo@propiq.com')
  const [password, setPassword] = useState('demo123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState<string | null>(null)

  const from = (location.state as { from?: string })?.from ?? '/dashboard'

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    const result = login(email, password)
    setLoading(false)
    if (result.ok) navigate(from, { replace: true })
    else setError(result.error)
  }

  const fillCredentials = (accEmail: string, accPassword: string) => {
    setEmail(accEmail)
    setPassword(accPassword)
    setError('')
  }

  const copyCreds = (accEmail: string, accPassword: string) => {
    navigator.clipboard.writeText(`${accEmail} / ${accPassword}`)
    setCopied(accEmail)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div className="flex min-h-screen bg-app-bg">
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden p-12 lg:flex">
        <div className="absolute inset-0 grainy-gradient-mint opacity-90" />
        <Link to="/" className="relative flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white">
            <span className="text-xs font-bold text-black">P</span>
          </div>
          <span className="text-lg font-semibold text-white">PropIQ</span>
        </Link>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative"
        >
          <h2 className="text-4xl font-semibold leading-tight tracking-tight text-white">
            Analyze smarter.
            <br />
            Invest with confidence.
          </h2>
          <p className="mt-4 max-w-md text-white/75">
            AI-powered property analysis — damage detection, deal metrics, and ranked investment insights.
          </p>
        </motion.div>
        <p className="relative text-xs text-white/50">© 2026 PropIQ</p>
      </div>

      <div className="flex flex-1 flex-col justify-center px-4 py-10 sm:px-6 sm:py-12 lg:px-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mx-auto w-full max-w-md"
        >
          <Link to="/" className="mb-8 flex items-center gap-2 lg:hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-black">
              <span className="text-xs font-bold text-white">P</span>
            </div>
            <span className="font-semibold text-black">PropIQ</span>
          </Link>

          <h1 className="text-2xl font-semibold tracking-tight text-black">Log in</h1>
          <p className="mt-2 text-sm text-app-muted">
            Don&apos;t have an account?{' '}
            <Link to="/register" className="font-medium text-black hover:underline">
              Sign up
            </Link>
          </p>

          {error && (
            <div className="mt-6 flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              {error}
            </div>
          )}

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <Button variant="primary" size="lg" type="submit" className="w-full" disabled={loading}>
              {loading ? 'Signing in...' : 'Log in'}
            </Button>
          </form>

          <Card className="mt-8" padding="sm">
            <p className="text-xs font-semibold uppercase tracking-wider text-app-muted">Demo accounts</p>
            <div className="mt-4 space-y-2">
              {DEMO_ACCOUNTS.map((acc) => (
                <div
                  key={acc.email}
                  className="flex flex-col gap-3 rounded-2xl border border-black/[0.06] bg-app-elevated px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
                >
                  <button type="button" onClick={() => fillCredentials(acc.email, acc.password)} className="min-w-0 flex-1 text-left">
                    <p className="text-sm font-medium text-black">{acc.user.name}</p>
                    <p className="break-all text-xs text-app-muted sm:break-normal">{acc.email} · {roleLabel(acc.user.role)}</p>
                  </button>
                  <button type="button" onClick={() => copyCreds(acc.email, acc.password)} className="self-end rounded-lg p-2 text-app-muted hover:bg-black/[0.04] sm:self-auto">
                    {copied === acc.email ? <CheckCircle2 className="h-4 w-4 text-emerald-600" /> : <Copy className="h-4 w-4" />}
                  </button>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
