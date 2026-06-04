import { Link } from 'react-router-dom'
import { StatCard } from '../components/ui/StatCard'
import { Card } from '../components/ui/Card'
import { StatusBadge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import {
  Building2,
  TrendingUp,
  DollarSign,
  Loader2,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertCircle,
  Plus,
} from 'lucide-react'
import {
  dashboardStats,
  mockProperties,
  formatCurrency,
  formatPercent,
  strategyLabels,
} from '../data/mockData'
import { useAuth, roleLabel } from '../context/AuthContext'

const activity = [
  { time: '2 hours ago', text: 'Analysis completed for 1842 Oakwood Drive', type: 'success' as const },
  { time: '5 hours ago', text: 'PDF report downloaded — 729 Riverside Blvd', type: 'info' as const },
  { time: 'Yesterday', text: 'New property submitted — 3301 Highland Park', type: 'pending' as const },
  { time: '2 days ago', text: 'Deal ranked #1 — 1842 Oakwood Drive (score 92)', type: 'success' as const },
]

const pipeline = [
  { stage: 'Draft', count: 1, color: 'bg-app-muted' },
  { stage: 'Analyzing', count: 1, color: 'bg-blue-500' },
  { stage: 'Complete', count: 3, color: 'bg-emerald-500' },
]

export function DashboardPage() {
  const { user } = useAuth()
  const recent = mockProperties.slice(0, 4)

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-black">Overview</h1>
          <p className="mt-1 text-sm text-app-muted">
            {user ? `${roleLabel(user.role)} dashboard` : 'Your investment pipeline at a glance'}
          </p>
        </div>
        <Button variant="primary" to="/dashboard/properties/new">
          <Plus className="h-4 w-4" />
          New Analysis
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          icon={Building2}
          label="Total Properties"
          value={String(dashboardStats.totalProperties)}
          change="+2 this month"
          positive
          index={0}
        />
        <StatCard
          icon={TrendingUp}
          label="Average ROI"
          value={formatPercent(dashboardStats.avgRoi)}
          change="+1.2% vs last month"
          positive
          index={1}
        />
        <StatCard
          icon={DollarSign}
          label="Total Profit Potential"
          value={formatCurrency(dashboardStats.totalProfit)}
          index={2}
        />
        <StatCard
          icon={Loader2}
          label="Active Analyses"
          value={String(dashboardStats.activeAnalyses)}
          index={3}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="font-medium text-black">Recent Properties</h2>
            <Button variant="ghost" size="sm" to="/dashboard/properties">
              View all
              <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </div>
          <div className="mt-6 space-y-4">
            {recent.map((p) => (
              <Link
                key={p.id}
                to={`/dashboard/properties/${p.id}`}
                className="flex items-center gap-4 rounded-xl border border-black/[0.06] bg-app-elevated p-4 transition-all hover:border-black/10 hover:shadow-sm"
              >
                <img
                  src={p.imageUrl}
                  alt={p.address}
                  className="h-14 w-20 rounded-lg object-cover"
                />
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium text-black">{p.address}</p>
                  <p className="text-sm text-app-muted">
                    {p.city}, {p.state} · {formatCurrency(p.listPrice)} · {p.beds}bd/{p.baths}ba
                  </p>
                </div>
                <div className="hidden text-right sm:block">
                  <p className="text-sm font-medium text-emerald-600">{formatPercent(p.roi)} ROI</p>
                  <p className="text-xs text-app-muted">{strategyLabels[p.strategy]}</p>
                </div>
                <StatusBadge status={p.status} />
              </Link>
            ))}
          </div>
        </Card>

        <div className="space-y-6">
          <Card>
            <h2 className="font-medium text-black">Pipeline</h2>
            <div className="mt-4 space-y-3">
              {pipeline.map(({ stage, count, color }) => (
                <div key={stage}>
                  <div className="flex justify-between text-sm">
                    <span className="text-app-subtle">{stage}</span>
                    <span className="font-medium text-black">{count}</span>
                  </div>
                  <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-black/[0.04]">
                    <div
                      className={`h-full rounded-full ${color}`}
                      style={{ width: `${(count / 5) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h2 className="font-medium text-black">Top Ranked Deals</h2>
            <div className="mt-6 space-y-4">
              {[...mockProperties]
                .sort((a, b) => b.rankScore - a.rankScore)
                .slice(0, 4)
                .map((p, i) => (
                  <div key={p.id} className="flex items-center gap-3">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-black/[0.04] text-sm font-medium text-app-subtle">
                      {i + 1}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-black">{p.address}</p>
                      <p className="text-xs text-app-muted">Score: {p.rankScore}/100</p>
                    </div>
                    <span className="text-sm font-medium text-emerald-600">{formatPercent(p.roi)}</span>
                  </div>
                ))}
            </div>
            <Button variant="outline" size="sm" to="/dashboard/rankings" className="mt-6 w-full">
              View rankings
            </Button>
          </Card>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="font-medium text-black">Recent Activity</h2>
          <div className="mt-6 space-y-4">
            {activity.map((item, i) => (
              <div key={i} className="flex gap-3">
                {item.type === 'success' && <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />}
                {item.type === 'info' && <Clock className="mt-0.5 h-4 w-4 shrink-0 text-blue-400" />}
                {item.type === 'pending' && <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />}
                <div>
                  <p className="text-sm text-black">{item.text}</p>
                  <p className="text-xs text-app-muted">{item.time}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <h2 className="font-medium text-black">Quick Actions</h2>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {[
              { label: 'Add property', to: '/dashboard/properties/new' },
              { label: 'Compare deals', to: '/dashboard/compare' },
              { label: 'View reports', to: '/dashboard/reports' },
              { label: 'See rankings', to: '/dashboard/rankings' },
            ].map(({ label, to }) => (
              <Link
                key={to}
                to={to}
                className="rounded-xl border border-black/[0.06] bg-app-elevated px-4 py-3 text-sm font-medium text-black transition-colors hover:border-black/10 hover:bg-app-surface"
              >
                {label}
              </Link>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
