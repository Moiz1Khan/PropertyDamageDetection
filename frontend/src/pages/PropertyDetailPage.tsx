import { Link, useParams } from 'react-router-dom'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Badge, StatusBadge } from '../components/ui/Badge'
import {
  ArrowLeft,
  Download,
  MapPin,
  AlertTriangle,
  Home,
  Target,
  Calendar,
  Ruler,
  Bed,
  Bath,
} from 'lucide-react'
import {
  mockProperties,
  formatCurrency,
  formatPercent,
  strategyLabels,
} from '../data/mockData'

const severityVariant = {
  low: 'success' as const,
  medium: 'warning' as const,
  high: 'danger' as const,
}

export function PropertyDetailPage() {
  const { id } = useParams()
  const property = mockProperties.find((p) => p.id === id) ?? mockProperties[0]

  const totalCost = property.listPrice + property.rehabCost
  const margin = property.arv - totalCost

  return (
    <div className="space-y-8">
      <div>
        <Link
          to="/dashboard/properties"
          className="mb-4 inline-flex items-center gap-2 text-sm text-app-muted hover:text-black"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to properties
        </Link>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-semibold tracking-tight text-black">{property.address}</h1>
              <StatusBadge status={property.status} />
              <Badge variant="info">Score {property.rankScore}/100</Badge>
            </div>
            <p className="mt-2 flex flex-wrap items-center gap-4 text-sm text-app-muted">
              <span className="flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" />
                {property.city}, {property.state}
              </span>
              <span>{property.type}</span>
              <span className="flex items-center gap-1">
                <Bed className="h-3.5 w-3.5" /> {property.beds} bed
              </span>
              <span className="flex items-center gap-1">
                <Bath className="h-3.5 w-3.5" /> {property.baths} bath
              </span>
              <span className="flex items-center gap-1">
                <Ruler className="h-3.5 w-3.5" /> {property.sqft.toLocaleString()} sqft
              </span>
              <span className="flex items-center gap-1">
                <Calendar className="h-3.5 w-3.5" /> Added {property.createdAt}
              </span>
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" to="/dashboard/compare">
              Compare
            </Button>
            <Button variant="primary">
              <Download className="h-4 w-4" />
              Download Report
            </Button>
          </div>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'List Price', value: formatCurrency(property.listPrice) },
          { label: 'Max Offer', value: formatCurrency(property.maxOffer), highlight: true },
          { label: 'Est. Profit', value: formatCurrency(property.profit), green: true },
          { label: 'ROI', value: formatPercent(property.roi), green: true },
        ].map(({ label, value, highlight, green }) => (
          <Card key={label} padding="sm">
            <p className="text-xs text-app-muted">{label}</p>
            <p className={`mt-1 text-xl font-semibold ${green ? 'text-emerald-600' : highlight ? 'text-black' : 'text-black'}`}>
              {value}
            </p>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="overflow-hidden rounded-2xl border border-black/[0.06] shadow-sm">
            <img
              src={property.imageUrl}
              alt={property.address}
              className="aspect-[21/9] w-full object-cover"
            />
          </div>

          <Card>
            <h2 className="flex items-center gap-2 font-medium text-black">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              Damage Detection (Computer Vision)
            </h2>
            <p className="mt-1 text-sm text-app-muted">
              {property.damages.length} issues detected across uploaded images
            </p>
            <div className="mt-4 space-y-3">
              {property.damages.map((d, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between rounded-xl border border-black/[0.06] bg-app-elevated px-4 py-3"
                >
                  <div>
                    <p className="text-sm font-medium text-black">{d.type}</p>
                    <p className="text-xs text-app-muted">{d.room}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="hidden w-24 sm:block">
                      <div className="h-1.5 overflow-hidden rounded-full bg-black/[0.04]">
                        <div
                          className="h-full rounded-full bg-amber-500"
                          style={{ width: `${d.score * 100}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-xs text-app-muted">{(d.score * 100).toFixed(0)}%</span>
                    <Badge variant={severityVariant[d.severity]}>{d.severity}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h2 className="font-medium text-black">Financial Breakdown</h2>
            <div className="mt-4 space-y-3 text-sm">
              {[
                { label: 'Purchase / List Price', value: formatCurrency(property.listPrice) },
                { label: 'Estimated Rehab', value: formatCurrency(property.rehabCost) },
                { label: 'Total Investment', value: formatCurrency(totalCost), bold: true },
                { label: 'After Repair Value (ARV)', value: formatCurrency(property.arv) },
                { label: 'Gross Margin', value: formatCurrency(margin), green: true },
                { label: 'Monthly Rent (est.)', value: `${formatCurrency(property.monthlyRent)}/mo` },
              ].map(({ label, value, bold, green }) => (
                <div key={label} className="flex justify-between border-b border-black/[0.06] pb-2 last:border-0">
                  <span className="text-app-muted">{label}</span>
                  <span className={`${bold ? 'font-semibold' : ''} ${green ? 'text-emerald-600' : 'text-black'}`}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h2 className="font-medium text-black">Comparable Properties</h2>
            <p className="mt-1 text-sm text-app-muted">Sales within 0.5 miles, last 6 months</p>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-black/[0.06] text-left text-app-muted">
                    <th className="pb-3 font-medium">Address</th>
                    <th className="pb-3 font-medium">Sale Price</th>
                    <th className="pb-3 font-medium">Sqft</th>
                    <th className="pb-3 font-medium">$/sqft</th>
                    <th className="pb-3 font-medium">Distance</th>
                    <th className="pb-3 font-medium">Sold</th>
                  </tr>
                </thead>
                <tbody>
                  {property.comps.map((c) => (
                    <tr key={c.id} className="border-b border-black/[0.06]/50">
                      <td className="py-3 text-black">{c.address}</td>
                      <td className="py-3">{formatCurrency(c.salePrice)}</td>
                      <td className="py-3">{c.sqft.toLocaleString()}</td>
                      <td className="py-3">${Math.round(c.salePrice / c.sqft)}</td>
                      <td className="py-3">{c.distance} mi</td>
                      <td className="py-3 text-app-muted">{c.soldDate}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <h2 className="font-medium text-black">Deal Summary</h2>
            <div className="mt-4 space-y-4">
              {[
                { label: 'List Price', value: formatCurrency(property.listPrice) },
                { label: 'Rehab Estimate', value: formatCurrency(property.rehabCost) },
                { label: 'ARV', value: formatCurrency(property.arv) },
                { label: 'Monthly Rent', value: formatCurrency(property.monthlyRent) },
                { label: 'Max Offer', value: formatCurrency(property.maxOffer), highlight: true },
                { label: 'Est. Profit', value: formatCurrency(property.profit), green: true },
                { label: 'ROI', value: formatPercent(property.roi), green: true },
              ].map(({ label, value, highlight, green }) => (
                <div key={label} className="flex justify-between text-sm">
                  <span className="text-app-muted">{label}</span>
                  <span className={`font-medium ${green ? 'text-emerald-600' : highlight ? 'text-black font-semibold' : 'text-black'}`}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h2 className="flex items-center gap-2 font-medium text-black">
              <Target className="h-4 w-4" />
              Recommended Strategy
            </h2>
            <p className="mt-3 text-lg font-medium text-black">{strategyLabels[property.strategy]}</p>
            <p className="mt-2 text-sm text-app-muted">
              Based on ROI ({formatPercent(property.roi)}), {formatPercent(property.neighborhood.appreciation)} area
              appreciation, and rental yield of {formatCurrency(property.monthlyRent)}/mo.
            </p>
            <div className="mt-4 rounded-xl bg-app-elevated px-4 py-3">
              <p className="text-xs text-app-muted">Rank Score</p>
              <p className="text-2xl font-semibold text-black">
                {property.rankScore}
                <span className="text-sm text-app-muted">/100</span>
              </p>
            </div>
          </Card>

          <Card>
            <h2 className="flex items-center gap-2 font-medium text-black">
              <Home className="h-4 w-4" />
              Neighborhood Analysis
            </h2>
            <div className="mt-4 space-y-3 text-sm">
              {[
                { label: 'Median Price', value: formatCurrency(property.neighborhood.medianPrice) },
                { label: 'Median Rent', value: `${formatCurrency(property.neighborhood.medianRent)}/mo` },
                { label: 'YoY Appreciation', value: formatPercent(property.neighborhood.appreciation), green: true },
                { label: 'School Rating', value: `${property.neighborhood.schoolRating}/10` },
                { label: 'Crime Index', value: String(property.neighborhood.crimeIndex), warn: property.neighborhood.crimeIndex > 30 },
              ].map(({ label, value, green, warn }) => (
                <div key={label} className="flex justify-between">
                  <span className="text-app-muted">{label}</span>
                  <span className={`${green ? 'text-emerald-600' : warn ? 'text-amber-400' : 'text-black'}`}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </Card>

          <Card padding="sm">
            <h2 className="text-sm font-medium text-black">Analysis Timeline</h2>
            <div className="mt-3 space-y-2 text-xs text-app-muted">
              <p>✓ Property data saved</p>
              <p>✓ CV damage scan complete</p>
              <p>✓ ML estimates generated</p>
              <p>✓ Comps fetched ({property.comps.length})</p>
              <p>✓ Deal metrics calculated</p>
              {property.status === 'complete' && <p className="text-emerald-600">✓ Report ready</p>}
              {property.status === 'analyzing' && <p className="text-blue-400">⋯ Analysis in progress...</p>}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
