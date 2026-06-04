import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { StatusBadge } from '../components/ui/Badge'
import { FileText, Download, Eye, Calendar, FileCheck } from 'lucide-react'
import { mockProperties, formatCurrency, formatPercent } from '../data/mockData'

export function ReportsPage() {
  const reports = mockProperties.filter((p) => p.status === 'complete')

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-black">Reports</h1>
        <p className="mt-1 text-sm text-app-muted">
          PDF investment summary reports for completed analyses · {reports.length} available
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { label: 'Total reports', value: String(reports.length) },
          { label: 'This month', value: '3' },
          { label: 'Last downloaded', value: '2 hrs ago' },
        ].map(({ label, value }) => (
          <Card key={label} padding="sm">
            <p className="text-xs text-app-muted">{label}</p>
            <p className="mt-1 text-2xl font-semibold text-black">{value}</p>
          </Card>
        ))}
      </div>

      <div className="grid gap-4">
        {reports.map((p) => (
          <Card key={p.id} className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-black/[0.04]">
                <FileText className="h-5 w-5 text-app-subtle" />
              </div>
              <div>
                <p className="font-medium text-black">Investment Summary — {p.address}</p>
                <p className="mt-1 text-sm text-app-muted">
                  {p.city}, {p.state} · ROI {formatPercent(p.roi)} · Profit {formatCurrency(p.profit)}
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-app-muted">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    Generated {p.createdAt}
                  </span>
                  <span className="flex items-center gap-1">
                    <FileCheck className="h-3 w-3" />
                    12 pages · PDF
                  </span>
                </div>
                <div className="mt-2 flex gap-2">
                  <StatusBadge status="complete" />
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm">
                <Eye className="h-4 w-4" />
                Preview
              </Button>
              <Button variant="primary" size="sm">
                <Download className="h-4 w-4" />
                Download PDF
              </Button>
            </div>
          </Card>
        ))}
      </div>

      <Card className="border-dashed">
        <div className="flex flex-col items-center py-8 text-center">
          <FileText className="h-10 w-10 text-app-muted" />
          <p className="mt-4 font-medium text-black">Generate a new report</p>
          <p className="mt-1 max-w-sm text-sm text-app-muted">
            Reports include deal metrics, damage findings, comps table, neighborhood overview, and strategy
            recommendation — suitable for lenders and partners.
          </p>
          <Button variant="outline" size="sm" to="/dashboard/properties" className="mt-6">
            View properties
          </Button>
        </div>
      </Card>

      <Card>
        <h2 className="font-medium text-black">Report contents</h2>
        <ul className="mt-4 grid gap-2 sm:grid-cols-2 text-sm text-app-subtle">
          {[
            'Executive summary & recommendation',
            'Property details & photos',
            'Damage detection results',
            'Rehab, ARV & rent estimates',
            'Comparable sales table',
            'Neighborhood analysis',
            'ROI, profit & max offer',
            'Risk factors & disclaimers',
          ].map((item) => (
            <li key={item} className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-black" />
              {item}
            </li>
          ))}
        </ul>
      </Card>
    </div>
  )
}
