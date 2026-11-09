import { useEffect, useState } from 'react'
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
  CheckCircle2,
  Plus,
} from 'lucide-react'
import { formatCurrency, formatPercent, strategyLabels } from '../data/mockData'
import { useAuth, roleLabel } from '../context/AuthContext'
import { api, type ApiProperty } from '../lib/api'

export function DashboardPage() {
  const { user } = useAuth()
  const [properties, setProperties] = useState<ApiProperty[]>([])
  const [stats, setStats] = useState({ totalProperties: 0, avgRoi: 0, totalProfit: 0, activeAnalyses: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.properties(), api.stats()])
      .then(([props, s]) => {
        setProperties(props)
        setStats(s)
      })
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [])

  const recent = properties.slice(0, 4)
  const pipeline = [
    { stage: 'Draft', count: properties.filter((p) => p.status === 'draft').length, color: 'bg-app-muted' },
    { stage: 'Analyzing', count: properties.filter((p) => p.status === 'analyzing').length, color: 'bg-blue-500' },
    { stage: 'Complete', count: properties.filter((p) => p.status === 'complete').length, color: 'bg-emerald-500' },
  ]
  const totalPipe = Math.max(properties.length, 1)

  if (loading) {
    return <p className="text-sm text-app-muted">Loading dashboard…</p>
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-black">Overview</h1>
          <p className="mt-1 text-sm text-app-muted">
            {user ? `${roleLabel(user.role)} dashboard` : 'Your investment pipeline at a glance'}
          </p>
        </div>
        <Button variant="primary" to="/dashboard/properties/new" className="w-full sm:w-auto">
          <Plus className="h-4 w-4" />
          New Analysis
        </Button>
      </div>

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard icon={Building2} label="Total Properties" value={String(stats.totalProperties)} index={0} />
        <StatCard icon={TrendingUp} label="Average ROI" value={formatPercent(stats.avgRoi)} positive index={1} />
        <StatCard icon={DollarSign} label="Total Profit Potential" value={formatCurrency(stats.totalProfit)} index={2} />
        <StatCard icon={Loader2} label="Active Analyses" value={String(stats.activeAnalyses)} index={3} />
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
            {recent.length === 0 && <p className="text-sm text-app-muted">No properties yet. Add your first analysis.</p>}
            {recent.map((p) => (
              <Link
                key={p.id}
                to={`/dashboard/properties/${p.id}`}
                className="flex flex-col gap-3 rounded-xl border border-black/[0.06] bg-app-elevated p-4 transition-all hover:border-black/10 hover:shadow-sm sm:flex-row sm:items-center sm:gap-4"
              >
                <div className="flex min-w-0 items-center gap-3 sm:gap-4">
                  <img src={p.imageUrl} alt={p.address} className="h-14 w-20 shrink-0 rounded-lg object-cover" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-black">{p.address}</p>
                    <p className="text-sm text-app-muted">
                      {p.city}, {p.state} · {formatCurrency(p.listPrice)} · {p.beds}bd/{p.baths}ba
                    </p>
                  </div>
                </div>
                <div className="flex items-center justify-between gap-3 sm:justify-end">
                  <div className="hidden text-right sm:block">
                    <p className="text-sm font-medium text-emerald-600">{formatPercent(p.roi)} ROI</p>
                    <p className="text-xs text-app-muted">{strategyLabels[p.strategy as keyof typeof strategyLabels] ?? p.strategy}</p>
                  </div>
                  <StatusBadge status={p.status as 'complete' | 'analyzing' | 'draft'} />
                </div>
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
                    <div className={`h-full rounded-full ${color}`} style={{ width: `${(count / totalPipe) * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h2 className="font-medium text-black">Top Ranked Deals</h2>
            <div className="mt-6 space-y-4">
              {[...properties]
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

      <Card>
        <h2 className="font-medium text-black">System status</h2>
        <div className="mt-4 flex items-center gap-2 text-sm text-emerald-700">
          <CheckCircle2 className="h-4 w-4" />
          Live API connected · analysis engine ready
        </div>
      </Card>
    </div>
  )
}
