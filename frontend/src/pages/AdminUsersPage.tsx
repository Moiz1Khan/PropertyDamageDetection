import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { StatusBadge } from '../components/ui/Badge'
import { Select } from '../components/ui/Input'
import { Search, UserPlus, MoreHorizontal, Shield } from 'lucide-react'
import { adminUsers } from '../data/mockData'

export function AdminUsersPage() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-black">User Management</h1>
          <p className="mt-1 text-sm text-app-muted">{adminUsers.length} registered users · Admin only</p>
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

      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-app-muted" />
          <input
            placeholder="Search users by name or email..."
            className="w-full rounded-xl border border-black/10 bg-app-surface py-3 pl-11 pr-4 text-sm text-black outline-none focus:border-black/20"
          />
        </div>
        <Select
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
        <table className="w-full min-w-[720px] text-sm">
          <thead>
            <tr className="border-b border-black/[0.06] bg-app-elevated text-left text-app-muted">
              <th className="p-4 font-medium">Name</th>
              <th className="p-4 font-medium">Email</th>
              <th className="p-4 font-medium">Role</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium">Joined</th>
              <th className="p-4 font-medium">Properties</th>
              <th className="p-4 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {adminUsers.map((u, i) => (
              <tr key={u.id} className="border-b border-black/[0.06]/50">
                <td className="p-4 font-medium text-black">{u.name}</td>
                <td className="p-4 text-app-muted">{u.email}</td>
                <td className="p-4">
                  <span className="rounded-full bg-black/[0.04] px-2.5 py-0.5 text-xs font-medium">{u.role}</span>
                </td>
                <td className="p-4">
                  <StatusBadge status={u.status as 'Active' | 'Pending'} />
                </td>
                <td className="p-4 text-app-muted">{u.joined}</td>
                <td className="p-4 text-black">{[12, 8, 5, 0, 1][i] ?? 0}</td>
                <td className="p-4">
                  <button type="button" className="text-app-muted hover:text-black">
                    <MoreHorizontal className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  )
}
