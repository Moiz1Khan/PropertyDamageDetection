import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import type { User, UserRole } from '../data/mockData'

interface AuthAccount {
  email: string
  password: string
  user: User
}

export const DEMO_ACCOUNTS: AuthAccount[] = [
  {
    email: 'demo@offmarketstream.com',
    password: 'demo123',
    user: { id: 'u1', name: 'Alex Morgan', email: 'demo@offmarketstream.com', role: 'investor' },
  },
  {
    email: 'agent@offmarketstream.com',
    password: 'agent123',
    user: { id: 'u2', name: 'Sarah Chen', email: 'agent@offmarketstream.com', role: 'agent' },
  },
  {
    email: 'admin@offmarketstream.com',
    password: 'admin123',
    user: { id: 'u4', name: 'Admin User', email: 'admin@offmarketstream.com', role: 'admin' },
  },
]

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  login: (email: string, password: string) => { ok: true } | { ok: false; error: string }
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

const STORAGE_KEY = 'offmarketstream_auth_user'

function loadStoredUser(): User | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as User) : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(loadStoredUser)

  const login = useCallback((email: string, password: string) => {
    const normalized = email.trim().toLowerCase()
    const account = DEMO_ACCOUNTS.find(
      (a) => a.email === normalized && a.password === password,
    )
    if (!account) {
      return { ok: false as const, error: 'Invalid email or password. Use the demo credentials below.' }
    }
    setUser(account.user)
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(account.user))
    return { ok: true as const }
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    sessionStorage.removeItem(STORAGE_KEY)
  }, [])

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export function roleLabel(role: UserRole) {
  return { investor: 'Property Investor', agent: 'Real Estate Agent', admin: 'Administrator' }[role]
}
