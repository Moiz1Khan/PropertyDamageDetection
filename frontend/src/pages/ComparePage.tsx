import { useState } from 'react'
import { Card } from '../components/ui/Card'
import { Check, Info } from 'lucide-react'
import { mockProperties, formatCurrency, formatPercent, strategyLabels } from '../data/mockData'

export function ComparePage() {
  const [selected, setSelected] = useState<string[]>(['p1', 'p2', 'p3'])

  const toggle = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : prev.length < 4 ? [...prev, id] : prev,
    )
  }

  const compared = mockProperties.filter((p) => selected.includes(p.id))

  const rows = [
    { label: 'List Price', key: 'listPrice' as const, format: formatCurrency },
    { label: 'Rehab Cost', key: 'rehabCost' as const, format: formatCurrency },
    { label: 'Total Cost', key: null, format: (p: (typeof mockProperties)[0]) => formatCurrency(p.listPrice + p.rehabCost) },
    { label: 'ARV', key: 'arv' as const, format: formatCurrency },
    { label: 'Monthly Rent', key: 'monthlyRent' as const, format: formatCurrency },
    { label: 'Profit', key: 'profit' as const, format: formatCurrency },
    { label: 'ROI', key: 'roi' as const, format: formatPercent },
    { label: 'Max Offer', key: 'maxOffer' as const, format: formatCurrency },
    { label: 'Rank Score', key: 'rankScore' as const, format: (n: number) => `${n}/100` },
    { label: 'Damages Found', key: null, format: (p: (typeof mockProperties)[0]) => String(p.damages.length) },
  ]

  const bestRoi = compared.length ? Math.max(...compared.map((p) => p.roi)) : 0

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-black">Compare Deals</h1>
        <p className="mt-1 text-sm text-app-muted">
          Select up to 4 properties to compare side-by-side across all key metrics
        </p>
      </div>

      <div className="flex items-start gap-3 rounded-xl border border-black/[0.06] bg-app-surface px-4 py-3 text-sm text-app-subtle">
        <Info className="mt-0.5 h-4 w-4 shrink-0" />
        Green highlights indicate the best ROI among selected properties. Use this view to shortlist offers.
      </div>

      <div className="flex flex-wrap gap-3">
        {mockProperties.map((p) => {
          const isSelected = selected.includes(p.id)
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => toggle(p.id)}
              className={`flex items-center gap-2 rounded-full border px-4 py-2 text-sm transition-colors ${
                isSelected
                  ? 'border-black bg-black text-white'
                  : 'border-black/[0.06] text-app-subtle hover:border-black/20 hover:text-black'
              }`}
            >
              {isSelected && <Check className="h-3.5 w-3.5" />}
              {p.address.split(',')[0]} ({formatPercent(p.roi)})
            </button>
          )
        })}
      </div>

      {compared.length >= 2 ? (
        <div className="table-scroll">
        <Card className="min-w-[640px] overflow-hidden p-0 sm:min-w-0">
          <table className="w-full min-w-[640px] text-sm">
            <thead>
              <tr className="border-b border-black/[0.06] bg-app-elevated">
                <th className="p-4 text-left font-medium text-app-muted">Metric</th>
                {compared.map((p) => (
                  <th key={p.id} className="p-4 text-left font-medium text-black">
                    <p>{p.address}</p>
                    <p className="mt-1 text-xs font-normal text-app-muted">
                      {p.city}, {p.state} · {p.sqft.toLocaleString()} sqft
                    </p>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-black/[0.06]/50">
                <td className="p-4 text-app-muted">Strategy</td>
                {compared.map((p) => (
                  <td key={p.id} className="p-4 text-black">{strategyLabels[p.strategy]}</td>
                ))}
              </tr>
              <tr className="border-b border-black/[0.06]/50">
                <td className="p-4 text-app-muted">Status</td>
                {compared.map((p) => (
                  <td key={p.id} className="p-4 capitalize text-black">{p.status}</td>
                ))}
              </tr>
              {rows.map(({ label, key, format }) => (
                <tr key={label} className="border-b border-black/[0.06]/50">
                  <td className="p-4 text-app-muted">{label}</td>
                  {compared.map((p) => {
                    const val = key ? (p[key] as number) : null
                    const display = key
                      ? (format as (n: number) => string)(val!)
                      : (format as (p: (typeof mockProperties)[0]) => string)(p)
                    const isBestRoi = key === 'roi' && p.roi === bestRoi
                    return (
                      <td
                        key={p.id}
                        className={`p-4 font-medium ${
                          isBestRoi || key === 'profit' ? 'text-emerald-600' : 'text-black'
                        } ${isBestRoi ? 'bg-emerald-50' : ''}`}
                      >
                        {display}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
        </div>
      ) : (
        <Card className="py-16 text-center">
          <p className="text-app-muted">Select at least 2 properties to compare</p>
        </Card>
      )}
    </div>
  )
}
