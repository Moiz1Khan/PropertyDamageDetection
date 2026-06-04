import { Link } from 'react-router-dom'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { StatusBadge } from '../components/ui/Badge'
import { Plus, Search, Filter, SlidersHorizontal } from 'lucide-react'
import { mockProperties, formatCurrency, formatPercent, strategyLabels } from '../data/mockData'

const filters = ['All', 'Complete', 'Analyzing', 'Flip', 'Rental']

export function PropertiesPage() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-black">Properties</h1>
          <p className="mt-1 text-sm text-app-muted">
            {mockProperties.length} properties · {mockProperties.filter((p) => p.status === 'complete').length} analyses complete
          </p>
        </div>
        <Button variant="primary" to="/dashboard/properties/new" className="w-full sm:w-auto">
          <Plus className="h-4 w-4" />
          Add Property
        </Button>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative min-w-0 flex-1">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-app-muted" />
          <input
            placeholder="Search by address, city, or ZIP..."
            className="w-full rounded-xl border border-black/10 bg-app-surface py-3 pl-11 pr-4 text-sm text-black outline-none focus:border-black/20"
          />
        </div>
        <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-row sm:gap-3">
        <Button variant="secondary" className="w-full">
          <Filter className="h-4 w-4" />
          Filters
        </Button>
        <Button variant="secondary" className="w-full">
          <SlidersHorizontal className="h-4 w-4" />
          Sort by ROI
        </Button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {filters.map((f, i) => (
          <button
            key={f}
            className={`rounded-full border px-4 py-1.5 text-xs font-medium transition-colors ${
              i === 0
                ? 'border-black bg-black text-white'
                : 'border-black/10 text-app-subtle hover:border-black/20 hover:text-black'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
        {mockProperties.map((p) => (
          <Link key={p.id} to={`/dashboard/properties/${p.id}`}>
            <Card hover className="h-full overflow-hidden p-0">
              <div className="relative aspect-[16/10] overflow-hidden">
                <img src={p.imageUrl} alt={p.address} className="h-full w-full object-cover" />
                <div className="absolute right-3 top-3">
                  <StatusBadge status={p.status} />
                </div>
                <div className="absolute bottom-3 left-3 rounded-full bg-black/70 px-2.5 py-1 text-xs font-medium text-white">
                  Score {p.rankScore}
                </div>
              </div>
              <div className="p-5">
                <h3 className="font-medium text-black">{p.address}</h3>
                <p className="mt-1 text-sm text-app-muted">
                  {p.city}, {p.state} · {p.beds} bed · {p.baths} bath · {p.sqft.toLocaleString()} sqft
                </p>
                <div className="mt-4 grid grid-cols-3 gap-2 border-t border-black/[0.06] pt-4 text-center">
                  <div>
                    <p className="text-xs text-app-muted">List</p>
                    <p className="text-sm font-medium text-black">{formatCurrency(p.listPrice)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-app-muted">ARV</p>
                    <p className="text-sm font-medium text-black">{formatCurrency(p.arv)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-app-muted">ROI</p>
                    <p className="text-sm font-medium text-emerald-600">{formatPercent(p.roi)}</p>
                  </div>
                </div>
                <p className="mt-3 text-xs text-app-muted">{strategyLabels[p.strategy]}</p>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
