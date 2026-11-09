import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '../components/ui/Button'
import { Input, Select } from '../components/ui/Input'
import { useAuth } from '../context/AuthContext'
import { AlertCircle } from 'lucide-react'

export function RegisterPage() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('investor')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    const result = await register({ name, email, password, role })
    setLoading(false)
    if (result.ok) navigate('/dashboard')
    else setError(result.error)
  }

  return (
    <div className="flex min-h-screen bg-app-bg">
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden p-12 lg:flex">
        <div className="absolute inset-0 grainy-gradient-warm opacity-90" />
        <Link to="/" className="relative flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white">
            <span className="text-[10px] font-bold text-black sm:text-xs">O</span>
          </div>
          <span className="text-lg font-semibold text-white">OffmarketStream</span>
        </Link>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h2 className="text-4xl font-semibold leading-tight text-white">
            Join data-driven
            <br />
            property investors
          </h2>
          <p className="mt-4 max-w-md text-white/75">
            Create your account and start analyzing properties with AI in minutes.
          </p>
        </motion.div>
        <p className="relative text-xs text-white/50">© 2026 OffmarketStream</p>
      </div>

      <div className="flex flex-1 flex-col justify-center px-4 py-10 sm:px-6 sm:py-12 lg:px-16">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mx-auto w-full max-w-md">
          <Link to="/" className="mb-8 flex items-center gap-2 lg:hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-black">
              <span className="text-[10px] font-bold text-white sm:text-xs">O</span>
            </div>
            <span className="font-semibold text-black">OffmarketStream</span>
          </Link>

          <h1 className="text-2xl font-semibold tracking-tight text-black">Create account</h1>
          <p className="mt-2 text-sm text-app-muted">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-black hover:underline">
              Log in
            </Link>
          </p>

          {error && (
            <div className="mt-6 flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              {error}
            </div>
          )}

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <Input label="Full name" value={name} onChange={(e) => setName(e.target.value)} required />
            <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <Select
              label="I am a..."
              value={role}
              onChange={(e) => setRole(e.target.value)}
              options={[
                { value: 'investor', label: 'Property Investor' },
                { value: 'agent', label: 'Real Estate Agent' },
                { value: 'lender', label: 'Lender' },
              ]}
            />
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
            <Button variant="primary" size="lg" type="submit" className="w-full" disabled={loading}>
              {loading ? 'Creating…' : 'Create account & continue'}
            </Button>
          </form>
        </motion.div>
      </div>
    </div>
  )
}
