import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  type ReactNode,
} from 'react'
import type { UserRole } from '../data/mockData'
import { api, getToken, setToken, type ApiUser } from '../lib/api'

export const DEMO_ACCOUNTS = [
  {
    email: 'demo@offmarketstream.com',
    password: 'demo123',
    user: { id: 'u1', name: 'Alex Morgan', email: 'demo@offmarketstream.com', role: 'investor' as UserRole },
  },
  {
    email: 'agent@offmarketstream.com',
    password: 'agent123',
    user: { id: 'u2', name: 'Sarah Chen', email: 'agent@offmarketstream.com', role: 'agent' as UserRole },
  },
  {
    email: 'admin@offmarketstream.com',
    password: 'admin123',
    user: { id: 'u4', name: 'Admin User', email: 'admin@offmarketstream.com', role: 'admin' as UserRole },
  },
]

type AuthUser = {
  id: string
  name: string
  email: string
  role: UserRole
}

interface AuthContextValue {
  user: AuthUser | null
  isAuthenticated: boolean
  loading: boolean
  login: (email: string, password: string) => Promise<{ ok: true } | { ok: false; error: string }>
  register: (payload: {
    name: string
    email: string
    password: string
    role?: string
  }) => Promise<{ ok: true } | { ok: false; error: string }>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

function toAuthUser(u: ApiUser): AuthUser {
  return {
    id: u.id,
    name: u.name,
    email: u.email,
    role: (u.role as UserRole) || 'investor',
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getToken()
    if (!token) {
      setLoading(false)
      return
    }
    api
      .me()
      .then((u) => setUser(toAuthUser(u)))
      .catch(() => {
        setToken(null)
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    try {
      const res = await api.login(email.trim().toLowerCase(), password)
      setToken(res.access_token)
      setUser(toAuthUser(res.user))
      return { ok: true as const }
    } catch (e) {
      return {
        ok: false as const,
        error: e instanceof Error ? e.message : 'Login failed. Start the API server and try demo credentials.',
      }
    }
  }, [])

  const register = useCallback(
    async (payload: { name: string; email: string; password: string; role?: string }) => {
      try {
        const res = await api.register(payload)
        setToken(res.access_token)
        setUser(toAuthUser(res.user))
        return { ok: true as const }
      } catch (e) {
        return {
          ok: false as const,
          error: e instanceof Error ? e.message : 'Registration failed',
        }
      }
    },
    [],
  )

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, loading, login, logout, register }}>
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
