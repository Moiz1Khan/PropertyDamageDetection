import { Link } from 'react-router-dom'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Trophy, TrendingUp, Info } from 'lucide-react'
import { mockProperties, formatCurrency, formatPercent, strategyLabels } from '../data/mockData'

const rankFactors = [
  { name: 'ROI weight', pct: 35 },
  { name: 'Margin of safety', pct: 25 },
  { name: 'Market appreciation', pct: 20 },
  { name: 'Damage / risk', pct: 20 },
]

export function RankingsPage() {
  const ranked = [...mockProperties].sort((a, b) => b.rankScore - a.rankScore)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-black">Deal Rankings</h1>
        <p className="mt-1 text-sm text-app-muted">
          Properties ranked by composite investment score (0–100)
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <div className="flex items-start gap-3 text-sm text-app-subtle">
            <Info className="mt-0.5 h-4 w-4 shrink-0" />
            Rankings combine ROI, profit margin, neighborhood trends, and damage severity into a single score.
          </div>
        </Card>
        <Card>
          <h2 className="text-sm font-medium text-black">Scoring weights</h2>
          <div className="mt-4 space-y-2">
            {rankFactors.map(({ name, pct }) => (
              <div key={name}>
                <div className="flex justify-between text-xs">
                  <span className="text-app-muted">{name}</span>
                  <span className="text-black">{pct}%</span>
                </div>
                <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-black/[0.04]">
                  <div className="h-full rounded-full bg-black" style={{ width: `${pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="space-y-4">
        {ranked.map((p, index) => (
          <Link key={p.id} to={`/dashboard/properties/${p.id}`}>
            <Card hover className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:p-6">
              <div className="flex min-w-0 items-start gap-3 sm:items-center sm:gap-4">
                <div
                  className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-base font-semibold sm:h-12 sm:w-12 sm:text-lg ${
                    index === 0
                      ? 'bg-amber-100 text-amber-700'
                      : index === 1
                        ? 'bg-black/[0.06] text-black'
                        : 'bg-black/[0.04] text-app-muted'
                  }`}
                >
                  {index === 0 ? <Trophy className="h-5 w-5" /> : index + 1}
                </div>
                <img
                  src={p.imageUrl}
                  alt={p.address}
                  className="h-14 w-20 shrink-0 rounded-lg object-cover sm:h-16 sm:w-24"
                />
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-black">{p.address}</p>
                  <p className="text-sm text-app-muted">
                    {p.city}, {p.state} · {formatCurrency(p.listPrice)}
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <Badge>{strategyLabels[p.strategy]}</Badge>
                    <Badge variant="default">{p.damages.length} damages</Badge>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 sm:flex sm:flex-1 sm:flex-wrap sm:items-center sm:justify-end sm:gap-6">
                <div className="text-center">
                  <p className="text-xs text-app-muted">Score</p>
                  <p className="text-xl font-semibold text-black">{p.rankScore}</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-app-muted">ROI</p>
                  <p className="text-xl font-semibold text-emerald-600">{formatPercent(p.roi)}</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-app-muted">Profit</p>
                  <p className="text-xl font-semibold text-black">{formatCurrency(p.profit)}</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-app-muted">Max Offer</p>
                  <p className="text-sm font-medium text-black">{formatCurrency(p.maxOffer)}</p>
                </div>
                <div className="hidden h-10 w-32 overflow-hidden rounded-full bg-black/[0.04] lg:block">
                  <div
                    className="flex h-full items-center justify-end bg-emerald-100 pr-2"
                    style={{ width: `${p.rankScore}%` }}
                  >
                    <TrendingUp className="h-4 w-4 text-emerald-600" />
                  </div>
                </div>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
