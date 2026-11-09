import { useEffect, useState } from 'react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { StatusBadge } from '../components/ui/Badge'
import { Select } from '../components/ui/Input'
import { Search, UserPlus, Shield } from 'lucide-react'
import { api, type ApiUser } from '../lib/api'

export function AdminUsersPage() {
  const [users, setUsers] = useState<ApiUser[]>([])
  const [query, setQuery] = useState('')
  const [role, setRole] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .adminUsers()
      .then(setUsers)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load users'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = users.filter((u) => {
    const q = query.toLowerCase()
    const matchesQ = !q || u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    const matchesRole = role === 'all' || u.role === role
    return matchesQ && matchesRole
  })

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-black">User Management</h1>
          <p className="mt-1 text-sm text-app-muted">{users.length} registered users · Admin only</p>
        </div>
        <Button variant="primary">
          <UserPlus className="h-4 w-4" />
          Add User
        </Button>
      </div>

      <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        <Shield className="mt-0.5 h-4 w-4 shrink-0" />
        This page is only accessible when logged in as admin@offmarketstream.com / admin123
      </div>

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-app-muted" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search users by name or email..."
            className="w-full rounded-xl border border-black/10 bg-app-surface py-3 pl-11 pr-4 text-sm text-black outline-none focus:border-black/20"
          />
        </div>
        <Select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          options={[
            { value: 'all', label: 'All roles' },
            { value: 'investor', label: 'Investor' },
            { value: 'agent', label: 'Agent' },
            { value: 'admin', label: 'Admin' },
            { value: 'lender', label: 'Lender' },
          ]}
        />
      </div>

      <Card className="table-scroll p-0">
        {loading ? (
          <p className="p-6 text-sm text-app-muted">Loading users…</p>
        ) : (
          <table className="w-full min-w-[720px] text-sm">
            <thead>
              <tr className="border-b border-black/[0.06] bg-app-elevated text-left text-app-muted">
                <th className="p-4 font-medium">Name</th>
                <th className="p-4 font-medium">Email</th>
                <th className="p-4 font-medium">Role</th>
                <th className="p-4 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((u) => (
                <tr key={u.id} className="border-b border-black/[0.06]/50">
                  <td className="p-4 font-medium text-black">{u.name}</td>
                  <td className="p-4 text-app-muted">{u.email}</td>
                  <td className="p-4 capitalize text-black">{u.role}</td>
                  <td className="p-4">
                    <StatusBadge status={(u.status === 'Active' ? 'complete' : 'draft') as 'complete' | 'draft'} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  )
}
