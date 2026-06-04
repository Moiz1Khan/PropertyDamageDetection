import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '../components/ui/Button'
import { Input, Select } from '../components/ui/Input'
import { useAuth, DEMO_ACCOUNTS } from '../context/AuthContext'

export function RegisterPage() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleDemoRegister = (e: React.FormEvent) => {
    e.preventDefault()
    const result = login('demo@offmarketstream.com', 'demo123')
    if (result.ok) navigate('/dashboard')
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
            <Link to="/login" className="font-medium text-black hover:underline">Log in</Link>
          </p>

          <form className="mt-8 space-y-5" onSubmit={handleDemoRegister}>
            <Input label="Full name" placeholder="Alex Morgan" />
            <Input label="Email" type="email" placeholder="you@example.com" />
            <Select label="I am a..." options={[
              { value: 'investor', label: 'Property Investor' },
              { value: 'agent', label: 'Real Estate Agent' },
              { value: 'lender', label: 'Lender' },
            ]} />
            <Input label="Password" type="password" placeholder="••••••••" />
            <Input label="Confirm password" type="password" placeholder="••••••••" />
            <p className="rounded-2xl bg-app-muted-bg px-4 py-3 text-xs text-app-muted">
              Demo: submits as <strong className="text-black">{DEMO_ACCOUNTS[0].email}</strong>
            </p>
            <Button variant="primary" size="lg" type="submit" className="w-full">
              Create account & continue
            </Button>
          </form>
        </motion.div>
      </div>
    </div>
  )
}
